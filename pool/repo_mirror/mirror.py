import os
import logging
from pathlib import Path
from cas_mirror.config import Config
from cas_mirror.exceptions import ConfigError
from cas_mirror.sync_pkgs import sync_pkgs
from cas_mirror.sync_files import sync_files
import tarfile


_logger = logging.getLogger(__file__)


def download_pkgs(config_file):
    # verify config; return if exception is raised
    try:
        config = Config(path=config_file)
    except ConfigError as e:
        _logger.error('Configuration Error in file {}: {}'.format(
            config_file,
            e.message
        ))
        return

    # sync packages; return if exception is raised
    try:
        sync_pkgs(config)
    except Exception as ex:
        _logger.error('Sync error: {}'.format(ex))
        return

    # fetch installers;
    if config.fetch_installers and config.remote_url:
        sync_files(config)
    else:
        _logger.info('Installer synchronization disabled or "remote_url" not set.')

    # return path for each channel
    return Path(config.mirror_dir)


def platform_tarballs(output_location: Path,
                      channel_dir: Path):
    """
    Expect folder to contain pkgs/{platform} with subfolder for each platform
    """
    tarballs = []
    mirror_dir = channel_dir.parent
    channel_name = channel_dir.parts[-1]
    for platform in channel_dir.glob('pkgs/*'):
        fname = channel_name + '-' + platform.parts[-1] + '.tar.gz'
        tarname = output_location.joinpath(fname)
        with tarfile.open(tarname.absolute().as_posix(), 'w:gz') as tgz:
            tgz.add(platform.absolute().as_posix(),
                    recursive=True,
                    arcname=platform.relative_to(mirror_dir))

        tarballs.append(tarname)

    return tarballs


def channel_tarballs(output_dir: Path,
                     channel_dir: Path):
    """
    Create tarball for each channel for all platforms

    :param output_dir:
    :param channel_dir:
    :return:
    """
    tarballs = []
    pass
