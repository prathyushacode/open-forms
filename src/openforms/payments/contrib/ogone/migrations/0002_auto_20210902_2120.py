# Generated by Django 2.2.24 on 2021-09-02 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments_ogone", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ogonemerchant",
            name="endpoint_custom",
            field=models.URLField(
                blank=True,
                help_text="Optionally override the preset endpoint",
                verbose_name="Custom endpoint",
            ),
        ),
        migrations.AlterField(
            model_name="ogonemerchant",
            name="endpoint_preset",
            field=models.URLField(
                choices=[
                    (
                        "https://ogone.test.v-psp.com/ncol/test/orderstandard_utf8.asp",
                        "Ogone Test",
                    ),
                    (
                        "https://secure.ogone.com/ncol/prod/orderstandard_utf8.asp",
                        "Ogone Live",
                    ),
                ],
                default="https://ogone.test.v-psp.com/ncol/test/orderstandard_utf8.asp",
                help_text="Select a common preset endpoint",
                verbose_name="Preset endpoint",
            ),
        ),
    ]
