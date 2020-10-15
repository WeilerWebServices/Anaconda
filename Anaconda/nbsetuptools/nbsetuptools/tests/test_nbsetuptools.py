import os
import tempfile
import unittest
from jupyter_core.paths import jupyter_config_dir
from ..nbsetuptools import NBSetup


class NBSetupTestCase(unittest.TestCase):
    def setUp(self):
        self.prefix = tempfile.mkdtemp()
        self.params = {
            'prefix': self.prefix,
            'static': os.path.join(os.path.dirname(__file__), 'support'),
        }

    def test_initialize(self):
        assert NBSetup('name').path == jupyter_config_dir()
        # assert NBSetup('name', prefix="/tmp").path == "/tmp/etc/jupyter"

    def test_install(self):
        nb_setup = NBSetup('name', **self.params)
        nb_setup.install()

        assert os.path.exists(
            os.path.join(self.prefix, 'share', 'jupyter', 'nbextensions', 'name'))

    def test_enable(self):
        nb_setup = NBSetup('name', **self.params)
        nb_setup.enable()

        for f in ['notebook.json', 'tree.json', 'edit.json']:
            assert os.path.exists(
                os.path.join(self.prefix, 'etc', 'jupyter', 'nbconfig', f)
            )


if __name__ == '__main__':
    unittest.main()
