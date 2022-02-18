import json
import os

from django.test import TestCase

from ...utils import iter_components

FILES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "files",
)


def load_json(filename: str):
    with open(os.path.join(FILES_DIR, filename), "r") as infile:
        return json.load(infile)


class BaseFormatterTestCase(TestCase):
    def assertFlatConfiguration(self, configuration):
        deep = [c["key"] for c in iter_components(configuration, recursive=True)]
        top = [c["key"] for c in iter_components(configuration, recursive=False)]

        if deep != top:
            nested = set(deep) - set(top)
            self.fail(
                f"expected flat configuration, found nested components: {list(sorted(nested))}"
            )

    def assertComponentKeyExists(self, configuration, key):
        assert isinstance(key, str)
        for component in iter_components(configuration):
            if component.get("key") == key:
                # pass
                return

        known = ", ".join(sorted(c.get("key") for c in iter_components(configuration)))
        self.fail(f"cannot find component '{key}' in {known}")
