from tox_ansible.filter.by_driver import ByDriver
from unittest import TestCase
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class TestByDriver(TestCase):
    def test_no_case(self):
        by_driver = ByDriver(['yes'])
        envlist = {
            'yes': Mock(tox_case=Mock(scenario=Mock(driver='yes'))),
            'no': Mock(tox_case=Mock(scenario=Mock(driver='no'))),
            'also_no': Mock(spec=[])
        }
        filtered = by_driver.filter(envlist)
        self.assertIn('yes', filtered)
        self.assertNotIn('no', filtered)
        self.assertNotIn('alsono', filtered)
