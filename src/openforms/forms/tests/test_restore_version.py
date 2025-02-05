import datetime

from django.test import TestCase
from django.utils.translation import gettext as _

from freezegun import freeze_time

from openforms.forms.models import FormDefinition, FormStep, FormVersion
from openforms.forms.tests.factories import (
    FormDefinitionFactory,
    FormFactory,
    FormStepFactory,
)

from .factories import FormVersionFactory
from .utils import EXPORT_BLOB


class RestoreVersionTest(TestCase):
    def test_restoring_version(self):
        form_definition = FormDefinitionFactory.create(
            name="Test Definition 2",
            internal_name="Test Internal 2",
            configuration={"test": "2"},
        )
        form = FormFactory.create(name="Test Form 2")
        FormStepFactory.create(form=form, form_definition=form_definition)

        version = FormVersion.objects.create(
            form=form,
            created=datetime.datetime(2021, 7, 21, 12, 00, 00),
            export_blob=EXPORT_BLOB,
        )

        self.assertEqual(1, FormVersion.objects.count())
        self.assertEqual(1, FormDefinition.objects.count())

        form.restore_old_version(version.uuid)
        form.refresh_from_db()

        self.assertEqual(
            2, FormVersion.objects.count()
        )  # the restore creates a new version itself
        self.assertEqual("Test Form 1", form.name)
        self.assertEqual("Test Form Internal 1", form.internal_name)
        self.assertEqual(2, FormDefinition.objects.count())
        last_version = FormVersion.objects.order_by("-created").first()
        self.assertEqual(
            last_version.description,
            _("Restored form version {version} (from {created}).").format(
                version=1, created=version.created.isoformat()
            ),
        )

        form_steps = FormStep.objects.filter(form=form)

        self.assertEqual(1, form_steps.count())

        restored_form_definition = form_steps.get().form_definition

        self.assertEqual("Test Definition 1", restored_form_definition.name)
        self.assertEqual(
            "Test Definition Internal 1", restored_form_definition.internal_name
        )
        self.assertEqual("test-definition-1", restored_form_definition.slug)
        self.assertEqual(
            {"components": [{"test": "1", "key": "test"}]},
            restored_form_definition.configuration,
        )

    @freeze_time("2022-02-21T17:00:00Z")
    def test_restore_version_description_correct(self):
        """
        Assert that the counting of the form version number works correctly.
        """
        form1, form2 = FormFactory.create_batch(2, generate_minimal_setup=True)
        form_version1 = FormVersion.objects.create_for(form=form1)
        form_version2 = FormVersion.objects.create_for(form=form2)

        for form_version in [form_version1, form_version2]:
            with self.subTest(form_version=form_version):
                self.assertEqual(
                    form_version.description, _("Version {number}").format(number=1)
                )

        with freeze_time("2022-02-21T18:00:00Z"):
            form_version3 = FormVersion.objects.create_for(form=form1)
            form_version4 = FormVersion.objects.create_for(form=form2)

            # check that restoring is correct
            for form, form_version in [
                (form1, form_version3),
                (form2, form_version4),
            ]:
                with self.subTest(form=form, form_version=form_version):
                    form.restore_old_version(form_version_uuid=form_version.uuid)
                    last_version = (
                        FormVersion.objects.filter(form=form)
                        .order_by("-created", "-pk")
                        .first()
                    )
                    self.assertEqual(
                        last_version.description,
                        _("Restored form version {version} (from {created}).").format(
                            version=2, created="2022-02-21T18:00:00+00:00"
                        ),
                    )

    def test_form_definition_same_slug_different_configuration(self):
        """Test that restoring a form definition with a slug that matches the slug of another form definition
        (but has a different configuration) creates a new form definition with a modified slug.
        """
        form_definition = FormDefinitionFactory.create(
            slug="test-definition-1", configuration={"test": "2"}
        )
        form = FormFactory.create(name="Test Form 2")
        FormStepFactory.create(form=form, form_definition=form_definition)

        version = FormVersion.objects.create(
            form=form,
            created=datetime.datetime(2021, 7, 21, 12, 00, 00),
            export_blob=EXPORT_BLOB,
        )

        form.restore_old_version(version.uuid)
        form.refresh_from_db()

        self.assertEqual(
            2, FormVersion.objects.count()
        )  # the restore creates a new version itself
        self.assertEqual(2, FormDefinition.objects.count())

        form_steps = FormStep.objects.filter(form=form)

        self.assertEqual(1, form_steps.count())

        restored_form_definition = form_steps.get().form_definition

        self.assertEqual("test-definition-1-2", restored_form_definition.slug)

    def test_handling_uuid(self):
        """
        Assert that existing UUIDs get replaced with new ones while restoring.

        Test what happens if the version being imported has the same definition UUID as
        another existing form definition.
        """
        form_definition = FormDefinitionFactory.create(
            uuid="f0dad93b-333b-49af-868b-a6bcb94fa1b8",
            slug="test-definition-1",
            configuration={"test": "2"},
        )
        form = FormFactory.create(name="Test Form 2")
        FormStepFactory.create(form=form, form_definition=form_definition)

        version = FormVersion.objects.create(
            form=form,
            created=datetime.datetime(2021, 7, 21, 12, 00, 00),
            export_blob=EXPORT_BLOB,
        )

        form.restore_old_version(version.uuid)
        form.refresh_from_db()

        new_fd = FormStep.objects.get(form=form).form_definition

        self.assertEqual(
            form_definition,
            FormDefinition.objects.get(uuid="f0dad93b-333b-49af-868b-a6bcb94fa1b8"),
        )
        self.assertNotEqual("f0dad93b-333b-49af-868b-a6bcb94fa1b8", str(new_fd.uuid))

    def test_restore_twice_a_version(self):
        form_definition = FormDefinitionFactory.create(
            slug="test-definition-2", configuration={"test": "2"}
        )
        form = FormFactory.create(name="Test Form 2")
        FormStepFactory.create(form=form, form_definition=form_definition)

        version = FormVersion.objects.create(
            form=form,
            created=datetime.datetime(2021, 7, 21, 12, 00, 00),
            export_blob=EXPORT_BLOB,
        )

        for _ in range(2):
            form.restore_old_version(version.uuid)
            form.refresh_from_db()

        self.assertEqual(2, FormDefinition.objects.count())

    def test_form_definition_same_slug_same_configuration(self):
        """Test that restoring a form definition with a slug that matches the slug of another form definition
        (and has the same configuration) links to the existing form definition.
        """
        form_definition = FormDefinitionFactory.create(
            slug="test-definition-1",
            configuration={"components": [{"test": "1", "key": "test"}]},
        )
        form = FormFactory.create(name="Test Form 2")
        FormStepFactory.create(form=form, form_definition=form_definition)

        version = FormVersion.objects.create(
            form=form,
            created=datetime.datetime(2021, 7, 21, 12, 00, 00),
            export_blob=EXPORT_BLOB,
        )

        form.restore_old_version(version.uuid)
        form.refresh_from_db()

        self.assertEqual(
            2, FormVersion.objects.count()
        )  # the restore creates a new version itself
        self.assertEqual(1, FormDefinition.objects.count())

        form_steps = FormStep.objects.filter(form=form)

        self.assertEqual(1, form_steps.count())

        restored_form_definition = form_steps.get().form_definition

        self.assertEqual(form_definition, restored_form_definition)

    def test_restore_form_with_reusable_form_definition(self):
        """
        Test that restoring forms with re-usable form definitions restores those as well.

        Regression test for issue #1348.
        """
        form = FormFactory.create(
            generate_minimal_setup=True,
            formstep__form_definition__is_reusable=True,
            formstep__form_definition__configuration={
                "components": [
                    {
                        "type": "textfield",
                        "key": "reusable1",
                    }
                ]
            },
        )
        FormStepFactory.create(
            form=form,
            form_definition__is_reusable=False,
            form_definition__configuration={
                "components": [
                    {
                        "type": "textfield",
                        "key": "notReusable",
                    }
                ]
            },
        )
        version = FormVersionFactory.create(form=form)
        # now delete the form step, we'll restore it in a bit
        form.formstep_set.all()[0].delete()
        with self.subTest("verify test setup"):
            self.assertNotEqual(version.export_blob, {})
            self.assertEqual(form.formstep_set.count(), 1)
            self.assertFalse(
                form.formstep_set.filter(form_definition__is_reusable=True).exists()
            )

        # do the actual restore
        form.restore_old_version(version.uuid)

        # get all fresh DB records
        form.refresh_from_db()

        self.assertEqual(form.formstep_set.count(), 2)
        form_steps = form.formstep_set.all()

        self.assertTrue(form_steps[0].form_definition.is_reusable)
        self.assertEqual(
            form_steps[0].form_definition.configuration,
            {
                "components": [
                    {
                        "type": "textfield",
                        "key": "reusable1",
                    }
                ]
            },
        )
        self.assertFalse(form_steps[1].form_definition.is_reusable)
