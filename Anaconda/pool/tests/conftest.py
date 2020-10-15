import pytest
from pathlib import Path


@pytest.fixture(scope="function")
def pkg_mirror(tmpdir):
    def _create_pkg_mirror(platforms):
        channel = tmpdir.mkdir('main')
        pkgs = channel.mkdir('pkgs')
        for platform in platforms:
            pkgs.mkdir(platform).strpath

        # return channel's directory name as str
        return Path(channel)

    return _create_pkg_mirror

