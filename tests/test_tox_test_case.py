from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock
from tox_ansible.tox_test_case import ToxTestCase
from tox_ansible.ansible.role import Role
from tox_ansible.ansible.scenario import Scenario
from tox_ansible.options import Options
from tox_ansible.tox_helper import Tox


DOCKER_DRIVER = {"driver": {"name": "docker"}}
OPENSTACK_DRIVER = {"driver": {"name": "openstack"}}
BASE_DEPS = ["molecule", "ansible-lint", "yamllint", "flake8", "pytest",
             "testinfra"]


@mock.patch.object(Scenario, "config", new_callable=mock.PropertyMock,
                   return_value={})
class TestToxTestCase(TestCase):
    @mock.patch.object(Options, "get_global_opts", return_value=[])
    @mock.patch.object(Tox, "posargs", new_callable=mock.PropertyMock,
                       return_value=[])
    def test_case_is_simple(self, pos_mock, opts_mock, config_mock):
        t = ToxTestCase(self.role, self.scenario)
        self.assertEqual(t.get_name(), "derp-my_test")
        self.assertEqual(t.get_working_dir(), "roles/derp")
        self.assertEqual(t.get_dependencies(), BASE_DEPS + ["ansible"])
        cmds = [["molecule", "test", "-s", self.scenario.name]]
        self.assertEqual(t.get_commands(self.opts), cmds)
        self.assertIsNone(t.get_basepython())

    @mock.patch.object(Options, "get_global_opts", return_value=["-c", "derp"])
    @mock.patch.object(Tox, "posargs", new_callable=mock.PropertyMock,
                       return_value=[])
    def test_case_has_global_opts(self, pos_mock, opts_mock, config_mock):
        t = ToxTestCase(self.role, self.scenario)
        cmds = [["molecule", "-c", "derp", "test", "-s", self.scenario.name]]
        self.assertEqual(t.get_commands(self.opts), cmds)

    def test_case_expand_ansible(self, config_mock):
        t = ToxTestCase(self.role, self.scenario)
        ts = t.expand_ansible("2.7")
        self.assertEqual(ts.ansible, "2.7")
        self.assertEqual(ts.get_name(), "ansible27-derp-my_test")
        self.assertEqual(ts.get_dependencies(), BASE_DEPS + ["ansible==2.7.*"])
        self.assertIsNone(ts.get_basepython())

    def test_case_expand_python(self, config_mock):
        t = ToxTestCase(self.role, self.scenario)
        ts = t.expand_python("4.1")
        self.assertEqual(ts.python, "4.1")
        self.assertEqual(ts.get_name(), "py41-derp-my_test")
        self.assertEqual(ts.get_basepython(), "python4.1")

    def test_case_expand_twice(self, config_mock):
        t = ToxTestCase(self.role, self.scenario)
        t1 = t.expand_python("4.1")
        t2 = t1.expand_ansible("1.0")
        self.assertEqual(t2.get_name(), "ansible10-py41-derp-my_test")

    @mock.patch.object(Scenario, "driver", new_callable=mock.PropertyMock,
                       return_value="docker")
    def test_case_includes_docker_deps(self, driver_mock, config_mock):
        s = Scenario("moelcule/my_test")
        t = ToxTestCase(self.role, s)
        self.assertIn("docker", t.get_dependencies())

    @mock.patch.object(Scenario, "driver", new_callable=mock.PropertyMock,
                       return_value="openstack")
    def test_case_includes_openstack_deps(self, driver_mock, config_mock):
        s = Scenario("molecule/osp_test")
        t = ToxTestCase(self.role, s)
        self.assertIn("openstacksdk", t.get_dependencies())

    @classmethod
    def setUp(cls):
        cls.role = Role("roles/derp")
        cls.scenario = Scenario("molecule/my_test")
        cls.opts = Options(mock.Mock())
