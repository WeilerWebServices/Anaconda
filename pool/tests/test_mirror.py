import pytest
from pathlib import Path
from repo_mirror import mirror


@pytest.mark.parametrize("platforms", [("win-64",),
                                       ("win-64", "linux-64", "osx-64", "noarch")])
def test_platform_tarballs(pkg_mirror, platforms):
    main_channel = pkg_mirror(platforms)
    tarballs = mirror.platform_tarballs(Path(), main_channel)

    # assert only tarball created for platform
    assert len(tarballs) == len(platforms)
    for platform in platforms:
        # ensure a tarball for each platform is created
        assert sum(map(lambda tar: platform in tar.parts[-1], tarballs))

    # remove the generated tarballs
    for tar in tarballs:
        try:
            tar.unlink()
        except FileNotFoundError:
            print(f'{tar.as_posix()} does not exist')
