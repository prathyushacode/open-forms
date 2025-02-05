"""
Bootstrap the environment.

Load the secrets from the .env file and store them in the environment, so
they are available for Django settings initialization.

.. warning::

    do NOT import anything Django related here, as this file needs to be loaded
    before Django is initialized.
"""
import logging
import os
import sys
import warnings
from pathlib import Path

from django.conf import settings

import defusedxml
import portalocker
import redis
from django_redis import get_redis_connection
from dotenv import load_dotenv
from requests import Session
from self_certifi import load_self_signed_certs as _load_self_signed_certs

logger = logging.getLogger(__name__)


def setup_env():
    # install defusedxml - note that this monkeypatches the stdlib and is experimental.
    # xmltodict only supports defusedexpat, which hasn't been updated since python 3.3
    defusedxml.defuse_stdlib()

    # load the environment variables containing the secrets/config
    dotenv_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env")
    load_dotenv(dotenv_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openforms.conf.dev")

    load_self_signed_certs()
    monkeypatch_requests()


def load_self_signed_certs() -> None:
    needs_extra_verify_certs = os.environ.get("EXTRA_VERIFY_CERTS")
    if not needs_extra_verify_certs:
        return

    _certs_initialized = bool(os.environ.get("REQUESTS_CA_BUNDLE"))
    if _certs_initialized:
        return

    # create target directory before hand and account for possible race conditions
    target_dir = Path(settings.SELF_CERTIFI_DIR)
    os.makedirs(target_dir, exist_ok=True)
    lockfile = target_dir / ".lock"

    # check if we have a valid connection - dev environments may not have redis running
    conn = get_redis_connection("portalocker")
    try:
        conn.ping()
    except redis.ConnectionError:
        if not settings.DEBUG:
            raise
        logger.warning(
            "Portalocker Redis connection is not alive, falling back to simple file lock"
        )
        lock = portalocker.TemporaryFileLock(lockfile)
    else:
        lock = portalocker.RedisLock(channel="load_self_signed_certs", connection=conn)

    try:
        # acquire lock - errors from timeouts should automatically lead to container restarts
        # and thus staggered initializations
        with lock:
            lockfile.touch()
            _load_self_signed_certs(str(target_dir))
            lockfile.unlink(missing_ok=True)
    except portalocker.AlreadyLocked:  # pragma:nocover
        logger.info("Could not acquire a self-certifi lock, exiting...")
        logger.debug(
            "On failure to acquire locks, your (container) orchestration should "
            "restart the container(s)"
        )
        sys.exit(1)

    _certs_initialized = True


def monkeypatch_requests():
    """
    Add a default timeout for any requests calls.
    """
    if hasattr(Session, "_original_request"):
        logger.debug(
            "Session is already patched OR has an ``_original_request`` attribute."
        )
        return

    Session._original_request = Session.request

    def new_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", settings.DEFAULT_TIMEOUT_REQUESTS)
        return self._original_request(*args, **kwargs)

    Session.request = new_request


def mute_deprecation_warnings():
    """
    Mute :class:`DeprecationWarning` again after O365 enabled them.

    See https://github.com/O365/python-o365/blob/master/O365/__init__.py for the culprit.

    See https://docs.python.org/3.8/library/warnings.html#overriding-the-default-filter
    for the stdlib documentation.
    """
    if not sys.warnoptions:
        warnings.simplefilter("ignore", DeprecationWarning, append=False)
