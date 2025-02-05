import logging

from django.dispatch import Signal, receiver

from rest_framework.request import Request

from openforms.submissions.models import Submission
from openforms.submissions.signals import submission_complete, submission_start

from .constants import FORM_AUTH_SESSION_KEY, AuthAttribute

logger = logging.getLogger(__name__)

#
# Custom signals
#
co_sign_authentication_success = Signal()
"""
Signal a succesful co-sign authentication.

Provides:
    :arg request: the HttpRequest instance
    :arg plugin: authentication plugin identifier
    :arg submission: The :class:`Submission` instance being co-signed.
"""


#
# Signal handlers
#


@receiver(submission_start, dispatch_uid="auth.set_submission_form_auth")
def set_auth_attribute_on_session(
    sender, instance: Submission, request: Request, **kwargs
):
    form_auth = request.session.get(FORM_AUTH_SESSION_KEY)
    if not form_auth:
        return

    plugin = form_auth["plugin"]
    attribute = form_auth["attribute"]
    assert (
        attribute in AuthAttribute.values
    ), f"Unexpected auth attribute {attribute} specified"
    # DO NOT log this in plain text, it is considered sensitive information (BSN for example)
    identifier = form_auth["value"]

    logger.debug(
        "Persisting form auth to submission %s. Plugin: '%s' (setting attribute '%s')",
        instance.uuid,
        plugin,
        attribute,
    )
    instance.auth_plugin = plugin
    setattr(instance, attribute, identifier)
    instance.save(update_fields=["auth_plugin", attribute])


@receiver(submission_complete, dispatch_uid="auth.clean_submission_form_auth")
def clean_submission_form_auth(sender, request: Request, **kwargs):
    if FORM_AUTH_SESSION_KEY not in request.session:
        return

    del request.session[FORM_AUTH_SESSION_KEY]
