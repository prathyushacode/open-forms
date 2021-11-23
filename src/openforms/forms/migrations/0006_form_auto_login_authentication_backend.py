# Generated by Django 2.2.24 on 2021-11-22 12:56

from django.db import migrations
import openforms.authentication.fields


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0005_form_confirmation_email_option"),
    ]

    operations = [
        migrations.AddField(
            model_name="form",
            name="auto_login_authentication_backend",
            field=openforms.authentication.fields.AuthenticationBackendChoiceField(
                blank=True, max_length=100, verbose_name="automatic login"
            ),
        ),
    ]
