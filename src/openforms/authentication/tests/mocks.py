from contextlib import contextmanager
from unittest.mock import PropertyMock, patch

from django.http import HttpResponse, HttpResponseRedirect

from ..base import BasePlugin
from ..registry import Registry


class Plugin(BasePlugin):
    verbose_name = "some human readable label"
    provides_auth = "dummy"

    def start_login(self, request, form, form_url):
        return HttpResponse("start")

    def handle_return(self, request, form):
        return HttpResponseRedirect(request.GET.get("next"))

    def handle_co_sign(self, request, form):
        return {
            "identifier": "mock-id",
            "fields": {
                "mock_field_1": "field 1",
                "mock_field_2": "",
            },
        }


class FailingPlugin(BasePlugin):
    verbose_name = "some human readable label"

    def start_login(self, request, form, form_url):
        raise Exception("start")

    def handle_return(self, request, form):
        raise Exception("return")


@contextmanager
def mock_register(register: Registry):
    patcher1 = patch(
        "openforms.authentication.views.AuthenticationStartView.register",
        new_callable=PropertyMock,
        return_value=register,
    )
    patcher2 = patch(
        "openforms.authentication.views.AuthenticationReturnView.register",
        new_callable=PropertyMock,
        return_value=register,
    )
    patcher3 = patch("openforms.submissions.serializers.register", new=register)
    with patcher1, patcher2, patcher3:
        yield
