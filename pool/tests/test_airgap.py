import pytest
from pathlib import Path
from ruamel_yaml import YAML
from repo_mirror.airgap import _default_mirror_configs, _parse_args


def test__default_mirror_configs_exception():
    """tests exception raised"""
    with pytest.raises(FileNotFoundError):
        _default_mirror_configs(Path("./not-exist"), "DEBUG")


def test__default_mirror_configs_jinja(tmpdir):
    """test jinja parsing is correct/valid"""
    ll = "DEBUG"
    mirror_dir = tmpdir.mkdir("mirror_dir")
    configs = _default_mirror_configs(Path(mirror_dir), ll)

    for conf in configs:
        assert conf.exists()
        with open(conf, 'r') as fp:
           yaml = YAML().load(fp)
           assert yaml["mirror_dir"].startswith(mirror_dir.strpath)
           assert yaml["log_dir"].startswith(mirror_dir.strpath)
           assert yaml["log_level"] == ll


#@pytest.mark.parametrize('mirror_dir', ['./'])
#def test__parse_args(mirror_dir):
#    sys.argv.append(mirror_dir)
#    args = _parse_args()
#    print(args)
