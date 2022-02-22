import json
import os
from datetime import date, datetime, time
from decimal import Decimal

from django.conf import settings
from django.test import SimpleTestCase
from django.utils import timezone

from ..type_mapping import to_python

FILES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "files",
)
FORMIO_FILES_DIR = os.path.join(
    settings.BASE_DIR,
    "src",
    "openforms",
    "formio",
    "formatters",
    "tests",
    "files",
)


def load_json(filename: str, files_dir=FILES_DIR):
    with open(os.path.join(files_dir, filename), "r") as infile:
        return json.load(infile)


class TypeMappingTests(SimpleTestCase):
    def test_kitchensink_types(self):
        all_components = load_json("kitchensink_components.json", FORMIO_FILES_DIR)[
            "components"
        ]
        data = load_json("kitchensink_data.json", FORMIO_FILES_DIR)

        skip_keys = [
            "updateNote",
        ]
        expected = {
            "bsn": "111222333",
            "bsnEmpty": "",
            "bsnHidden": "111222333",
            "bsnMulti": ["111222333", "123456782"],
            "bsnMultiEmpty": [None],
            "checkbox": True,
            "checkboxDefault": True,
            "checkboxEmpty": False,
            "checkboxHidden": True,
            "currency": Decimal("1234.56"),
            "currencyHidden": Decimal("123"),
            "currencyDecimal": Decimal("1234.56"),
            "currencyDecimalHidden": Decimal("123.45"),
            "currencyDecimalMulti": [
                Decimal("1234.56"),
                Decimal("1"),
                Decimal("0"),
            ],
            "currencyMulti": [
                Decimal("1234.56"),
                Decimal("1"),
                Decimal("0"),
            ],
            "currencyMultiEmpty": [None],
            "date": date(2022, 2, 14),
            "dateEmpty": None,
            "dateHidden": date(2022, 2, 14),
            "dateMulti": [
                date(2022, 2, 14),
                date(2022, 2, 15),
                date(2022, 2, 16),
            ],
            "dateMultiEmpty": [None],
            "email": "test@example.com",
            "emailEmpty": "",
            "emailHidden": "test@example.com",
            "emailMulti": ["aaa@aaa.nl", "bbb@bbb.nl"],
            "emailMultiDefault": ["aaa@aaa.nl", "bbb@bbb.nl"],
            "emailMultiEmpty": [None],
            "file": [
                {
                    "data": {
                        "baseUrl": "http://localhost:8000/api/v1/",
                        "form": "",
                        "name": "blank.doc",
                        "project": "",
                        "size": 1048576,
                        "url": "http://localhost:8000/api/v1/submissions/files/35527900-8248-4e75-a553-c2d1039a002b",
                    },
                    "name": "blank-65faf10b-afaf-48af-a749-ff5780abf75b.doc",
                    "originalName": "blank.doc",
                    "size": 1048576,
                    "storage": "url",
                    "type": "application/msword",
                    "url": "http://localhost:8000/api/v1/submissions/files/35527900-8248-4e75-a553-c2d1039a002b",
                }
            ],
            "fileUploadEmpty": [],
            "fileUploadHidden": [],
            "fileUploadMulti": [
                {
                    "data": {
                        "baseUrl": "http://localhost:8000/api/v1/",
                        "form": "",
                        "name": "blank.doc",
                        "project": "",
                        "size": 1048576,
                        "url": "http://localhost:8000/api/v1/submissions/files/a2444b75-dc1a-4363-a482-286579992768",
                    },
                    "name": "blank-428299d9-9aa3-4b31-a908-dc87f91ba1b0.doc",
                    "originalName": "blank.doc",
                    "size": 1048576,
                    "storage": "url",
                    "type": "application/msword",
                    "url": "http://localhost:8000/api/v1/submissions/files/a2444b75-dc1a-4363-a482-286579992768",
                },
                {
                    "data": {
                        "baseUrl": "http://localhost:8000/api/v1/",
                        "form": "",
                        "name": "dummy.doc",
                        "project": "",
                        "size": 1048576,
                        "url": "http://localhost:8000/api/v1/submissions/files/9ecc3688-5975-4b3f-b0e3-d312613fb6de",
                    },
                    "name": "dummy-82450592-32d1-4efa-b2f0-a0c024571df4.doc",
                    "originalName": "dummy.doc",
                    "size": 1048576,
                    "storage": "url",
                    "type": "application/msword",
                    "url": "http://localhost:8000/api/v1/submissions/files/9ecc3688-5975-4b3f-b0e3-d312613fb6de",
                },
            ],
            "fileUploadMultiEmpty": [],
            "iban": "NL02ABNA0123456789",
            "ibanEmpty": "",
            "ibanHidden": "NL02ABNA0123456789",
            "ibanMulti": ["NL02ABNA0123456789", "BE71096123456769"],
            "ibanMultiEmpty": [None],
            "licensePlateEmpty": "",
            "licensePlateHidden": "aa-bb-12",
            "licensePlateMulti": ["aa-bb-12", "1-aaa-12", "12-aa-34"],
            "licensePlateMultiEmpty": [None],
            "licenseplate": "aa-bb-12",
            "map": [52.373087283242505, 4.8923054658521945],
            "mapEmpty": [52.379648, 4.9020928],
            "mapHidden": [52.379648, 4.9020928],
            "number": 1234,
            "numberHidden": 1234,
            "numberDecimal": 1234.56,
            "numberDecimalMulti": [1234.56, 100, 12.3, 1, 0],
            "numberMulti": [123123123, 123, 1, 0],
            "numberMultiEmpty": [None],
            "password": "secret",
            "passwordEmpty": "",
            "passwordHidden": "secret",
            "passwordMulti": ["secret", "password"],
            "passwordMultiEmpty": [None],
            "phoneNumber": "0123456789",
            "phoneNumberEmpty": "",
            "phoneNumberHidden": "0123456789",
            "phoneNumberMulti": ["0123456789", "0123456780"],
            "phoneNumberMultiEmpty": [None],
            "postcode": "1234 ab",
            "postcodeEmpty": "",
            "postcodeHidden": "1234 ab",
            "postcodeMulti": ["1234 ab", "4321 ba"],
            "postcodeMultiEmpty": [None],
            "radio": "aaa",
            "radioEmpty": "",
            "radioHidden": "aaa",
            "select": "aaa",
            "selectBoxes": ["aaa", "bbb"],
            "selectBoxesEmpty": [],
            "selectBoxesHidden": ["aaa"],
            "selectEmpty": "",
            "selectHidden": "aaa",
            "selectMulti": ["aaa", "bbb"],
            "selectMultiEmpty": [],
            "signature": "data:image/png;base64,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",
            "signatureEmpty": "",
            "signatureHidden": "",
            "textArea": "text with newline\ntext with blank line\n\ntext with newline\ntext with double blank line\n\n\ntext with newline\n",
            "textAreaEmpty": "",
            "textAreaHidden": "line 1\n\nline 2\n",
            "textAreaMulti": ["text no newline", "single line with newline\n"],
            "textAreaMultiEmpty": [""],
            "textField": "lower case text",
            "textFieldEmpty": "",
            "textFieldHidden": "lower case text",
            "textFieldMulti": ["lower case text", "Upper Case Text"],
            "textFieldMultiDefault": ["aaa", "bbb"],
            "textFieldMultiEmpty": [None],
            "time": time(12, 34),
            "timeEmpty": None,
            "timeHidden": time(12, 34),
            "timeMulti": [
                time(12, 34),
                time(21, 43),
            ],
            "timeMultiEmpty": [None],
        }

        for component in all_components:
            key = component["key"]
            if key in skip_keys:
                continue

            value = data.get(key, "NOT_IN_DATA")
            expected_python_value = expected.get(key, "NOT_EXPECTED")

            with self.subTest(
                component=component["key"], value=value, expected=expected_python_value
            ):
                result = to_python(component, value)

                self.assertEqual(result, expected_python_value)

    def test_all_types(self):
        all_components = load_json("all_components.json")["components"]
        data = load_json("all_components_data.json")
        expected = {
            "bsn": "123456782",
            "map": [52.3782943985417, 4.899629917973432],
            "date": date(2021, 12, 24),
            "file": [],
            "iban": "RO09 BCYP 0000 0012 3456 7890",
            "time": time(16, 26),
            "email": "test@example.com",
            "radio": "option2",
            "number": 42.123,
            "select": "option1",
            "password": "secret",
            "postcode": "1234 AA",
            "textArea": "Textarea test",
            "signature": "data:image/png;base64,iVBO[truncated]",
            "textField": "Simple text input",
            "phoneNumber": "+31633924456",
            "selectBoxes": ["option1", "option2"],
            "licenseplate": "1-AAA-BB",
            "select2": date(2021, 12, 29),
            "select3": datetime(2021, 12, 29, 7, 15).replace(tzinfo=timezone.utc),
        }

        for component in all_components:
            key = component["key"]
            value = data[key]
            expected_python_value = expected[key]

            with self.subTest(
                component=component["key"], value=value, expected=expected_python_value
            ):
                result = to_python(component, value)

                self.assertEqual(result, expected_python_value)

    def test_multiple_component(self):
        component = {
            "type": "number",
            "multiple": True,
        }

        result = to_python(component, [42, 420.69])

        self.assertEqual(result, [42, 420.69])

    def test_appointment_select_product(self):
        component = {
            "type": "select",
            "appointments": {
                "showProducts": True,
            },
        }
        value = {"name": "Example name", "identifier": "123"}

        result = to_python(component, value)

        self.assertEqual(result, value)

    def test_partial_appointment_config(self):
        component = {"type": "select", "appointments": {"showDates": False}}
        value = "option1"

        result = to_python(component, value)

        self.assertEqual(result, "option1")
