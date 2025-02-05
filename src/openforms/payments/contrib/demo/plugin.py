from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from ...base import BasePlugin, PaymentInfo
from ...constants import PaymentStatus
from ...registry import register


@register("demo")
class DemoPayment(BasePlugin):
    verbose_name = _("Demo")
    is_demo_plugin = True

    def start_payment(self, request, payment):
        url = self.get_return_url(request, payment)
        return PaymentInfo(url=url, data={})

    def handle_return(self, request, payment):
        payment.status = PaymentStatus.completed
        payment.save()
        return HttpResponseRedirect(payment.submission.form_url)

    def check_config(self):
        """
        Demo config is always valid.
        """
        pass
