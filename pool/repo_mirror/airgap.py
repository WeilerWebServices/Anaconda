import time
import logging
from typing import Tuple
from argparse import ArgumentParser
from pathlib import Path
from jinja2 import Environment, PackageLoader
from .log import initialize_log
from .mirror import download_pkgs, platform_tarballs
from .pool import upload_files


_logger = logging.getLogger(__file__)


def _default_mirror_configs(mirror_dir: Path, log_level: str) -> Tuple[Path]:
    """
    Load jinja templates for configs included with the package

    :rtype: tuple[Path]
    :return: paths to config files: (anaconda.yaml, r.yaml, msys2.yaml)
    """
    env = Environment(loader=PackageLoader('repo_mirror', 'templates'))

    configs = []
    for name in ('anaconda.yaml', 'r.yaml', 'msys2.yaml'):
        temp = env.get_template(name)
        cf = mirror_dir.joinpath(temp.name)

        temp.stream(mirror_dir=mirror_dir.as_posix(),
                    log_dir=mirror_dir.as_posix(),
                    log_level=log_level).dump(cf.as_posix())

        configs.append(cf)

    return configs


def _parse_args():
    parser = ArgumentParser(description="create airgap archive of conda channels")

    parser.add_argument('mirror_dir',
                        nargs='?',
                        default=Path(),
                        type=Path,
                        help='(default: cwd) packages get mirrored here')
    parser.add_argument('-f',
                        '--file',
                        nargs='+',
                        dest='mirror_configs',
                        default=[],
                        type=Path,
                        help='load mirror config yaml files from this directory')
    parser.add_argument('-m',
                        '--mirror-only',
                        dest='mirror_only',
                        action='store_true',
                        default=False,
                        help='create mirror of conda packages then exit')
    parser.add_argument('-l',
                        '--log-level',
                        dest='log_level',
                        action='store',
                        default='INFO',
                        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help='log-level of ERROR, WARNING, INFO, DEBUG.'
                             'Default is INFO.')
    parser.add_argument('-b',
                        '--aws-bucket',
                        dest='aws_bucket',
                        action='store',
                        default='airgap.svc.anaconda.com',
                        help='aws bucket to which the tarballs are uploaded')
    parser.add_argument('-n',
                        '--upload-folder',
                        dest='folder_name',
                        action='store',
                        default=time.strftime("%Y_%m"),
                        help='upload to this folder; mostly for testing')
    args = parser.parse_args()

    # generate default yaml config files in mirror_dir
    if not args.mirror_configs:
        args.mirror_configs = \
            _default_mirror_configs(args.mirror_dir, args.log_level)

    return args


def main():
    args = _parse_args()

    initialize_log(args.log_level)
    _logger.info('initialized logger')

    # TODO: this is hacky; we should fix logging in cas_mirror
    for name in ('fetch.start', 'fetch.update', 'fetch.stop'):
        lgr = logging.getLogger(name)
        lgr.setLevel(logging.ERROR)

    # mirror packages
    channels = []   # list of Path objects
    tarballs = []   # list of Path objects
    for config_file in args.mirror_configs:
        channel = download_pkgs(config_file)
        channel_tarballs = platform_tarballs(args.mirror_dir, channel)
        tarballs.extend(channel_tarballs)
        channels.append(channel)

    # verify mirror - any testing of the mirror after creation?

    # upload it to AWS
    if args.mirror_only:
        return

    files_to_upload = args.mirror_configs
    files_to_upload.extend(tarballs)

    # upload files
    upload_files(args.aws_bucket, args.folder_name, files_to_upload)


if __name__ == '__main__':
    main()
