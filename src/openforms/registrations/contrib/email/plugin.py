import html
from mimetypes import types_map
from typing import List, NoReturn, Tuple

from django.conf import settings
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from openforms.emails.utils import send_mail_html, strip_tags_plus
from openforms.submissions.exports import create_submission_export
from openforms.submissions.models import Submission
from openforms.submissions.tasks.registration import set_submission_reference

from ...base import BasePlugin
from ...exceptions import NoSubmissionReference
from ...registry import register
from .checks import check_config
from .config import EmailOptionsSerializer
from .constants import AttachmentFormat
from .presentation import SubmittedDataWrapper


@register("email")
class EmailRegistration(BasePlugin):
    verbose_name = _("Email registration")
    configuration_options = EmailOptionsSerializer

    def register_submission(self, submission: Submission, options: dict) -> None:
        # explicitly get a reference before registering
        set_submission_reference(submission)

        subject = _("[Open Forms] {form_name} - submission {public_reference}").format(
            form_name=submission.form.admin_name,
            public_reference=submission.public_registration_reference,
        )
        self.send_registration_email(options["to_emails"], subject, submission, options)

    def send_registration_email(
        self,
        recipients,
        subject,
        submission: Submission,
        options: dict,
        extra_context=None,
    ):
        # extract the formatted data first
        printable_data: list = submission.get_printable_data()
        # get the attachment data, keyed by form component key, value is a model instance
        attachments = submission.get_merged_attachments()
        # these are not related to each other now, but we can iterate over the components
        # by keys and inject the file information again so we can generate URLs to
        # download the files.
        display_data = []

        # get_printable_data relies on ``get_ordered_data_with_component_type``
        for (key, info), (label, display) in zip(
            submission.get_ordered_data_with_component_type().items(), printable_data
        ):
            is_file = info.get("type") == "file"
            if is_file:
                files = attachments.get(key, [])
                display = SubmittedDataWrapper(is_file=True, value=files)
            else:
                display = SubmittedDataWrapper(is_file=False, value=display)

            display_data.append((label, display))

        context = {
            "form_name": submission.form.admin_name,
            "public_reference": submission.public_registration_reference,
            "datetime": timezone.localtime(submission.completed_on).strftime(
                "%H:%M:%S %d-%m-%Y"
            ),
            "submitted_data": display_data,
        }
        if extra_context:
            context.update(extra_context)

        html_template = get_template("emails/email_registration.html")
        text_template = get_template("emails/email_registration.txt")

        html_content = html_template.render(context)
        context["rendering_text"] = True
        text_content = text_template.render(context)

        # post process since the mail template has html markup and django escaped entities
        text_content = strip_tags_plus(text_content)
        text_content = html.unescape(text_content)

        attachment_formats = options.get("attachment_formats", [])
        attachments = []
        for attachment_format in attachment_formats:
            mime_type = types_map[f".{attachment_format}"]
            if attachment_format in [AttachmentFormat.csv, AttachmentFormat.xlsx]:
                export_data = create_submission_export(
                    Submission.objects.filter(pk=submission.pk)
                ).export(attachment_format)

                attachment = (
                    f"{submission.form.admin_name} - submission.{attachment_format}",
                    export_data,
                    mime_type,
                )
                attachments.append(attachment)
            elif attachment_format == AttachmentFormat.pdf:
                attachment = (
                    f"{submission.report.title}.pdf",
                    submission.report.content.read(),
                    mime_type,
                )
                attachments.append(attachment)

        send_mail_html(
            subject,
            html_content,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
            attachment_tuples=attachments,
            text_message=text_content,
        )

    def get_reference_from_result(self, result: None) -> NoReturn:
        raise NoSubmissionReference("Email plugin does not emit a reference")

    def update_payment_status(self, submission: "Submission", options: dict):
        subject = _(
            "[Open Forms] {form_name} - submission payment received {public_reference}"
        ).format(
            form_name=submission.form.admin_name,
            public_reference=submission.public_registration_reference,
        )
        recipients = options.get("payment_emails")
        if not recipients:
            recipients = options["to_emails"]

        extra_context = {
            # switch in the template
            "payment_received": True,
            # note: it is not a feature (yet) but the model supports multiple payments
            "payment_order_id": ", ".join(
                map(str, submission.payments.get_completed_public_order_ids())
            ),
        }
        self.send_registration_email(
            recipients, subject, submission, options, extra_context
        )

    def check_config(self):
        check_config()

    def get_config_actions(self) -> List[Tuple[str, str]]:
        return [
            (_("Test"), reverse("admin_email_test")),
        ]
