# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import copy
import errno
import os
from os.path import join, isdir
import sys

try:
    try:
        from inspect import signature
    except ImportError:
        from funcsigs import signature
    from jupyter_core.paths import jupyter_config_dir
    from notebook.nbextensions import install_nbextension
    from notebook.services.config import ConfigManager
except ImportError:
    # when a Conda environment is removed, dependencies may be
    # unlinked first. In this case, just bail. The Jupyter
    # config where this extension is registered lives in the
    # environment, so it will be destroyed anyway.
    # (If we allow this to fail, it will show up as a build
    # failure on anaconda.org CI system).
    sys.exit(0)

class StaticPathNotFound(Exception):
    pass


def mkdir_p(path):
    """ 'mkdir -p' in Python """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and isdir(path):
            pass
        else:
            raise


class NBSetup(object):
    extensions_map = {
        'notebook': 'main.js',
        'tree': 'tree.js',
        'edit': 'edit.js'
    }

    def __init__(self, name, **kwargs):
        self.name = name
        self.prefix = kwargs.get('prefix', None)
        self.kwargs = kwargs
        if self.prefix is None:
            self.path = jupyter_config_dir()
        else:
            self.path = join(self.prefix, "etc", "jupyter")
        self.cm = ConfigManager(config_dir=join(self.path, 'nbconfig'))
        self.cm_server = ConfigManager(config_dir=self.path)

    def install(self):
        """
        Install an extension (copy or symlinks)
        """
        try:
            install_nbextension(self.kwargs['static'], **self._install_params())
            self._echo("Installing {}".format(self.name), 'ok')
        except Exception as e:
            self._echo(e, None)
            self._echo("Installing {}".format(self.name), 'fail')

    def enable(self):
        mkdir_p(self.cm.config_dir)
        self._enable_client_extensions()
        try:
            __import__(self.name)
            self._enable_server_extensions()
        except ImportError:
            pass
        self._echo('Enabling {}'.format(self.name), 'ok')

    def disable(self):
        # Client side
        self._disable_client_extension()
        self._disable_server_extension()

    def _disable_client_extension(self):
        for _type, filename in list(self.extensions_map.items()):
            cfg = self.cm.get(_type)
            try:
                nb_key = "{}/{}".format(self.name, filename[:-3])
                nb_extensions = list(cfg['load_extensions'].keys())
                if nb_key in nb_extensions:
                    cfg['load_extensions'].pop(nb_key)
                    self.cm.set(_type, cfg)
                    self._echo("Disabling {} as {}".format(self.name, _type), 'ok')
            except KeyError:
                self._echo("{} wasn't enabled as a {}. Nothing to do.".format(self.name, _type))

    def _disable_server_extension(self):
        cfg = self.cm_server.get("jupyter_notebook_config")
        try:
            server_extensions = cfg["NotebookApp"]["server_extensions"]
            if "{}.nbextension".format(self.name) in server_extensions:
                server_extensions.remove("{}.nbextension".format(self.name))
            self.cm_server.update("jupyter_notebook_config", cfg)
            self._echo("{} was disabled as a server extension".format(self.name), 'ok')
        except KeyError:
            self._echo("{} was't enabled as a server extension. Nothing to do.".format(self.name))

    def _install_params(self):
        params = copy.deepcopy(self.kwargs)
        params['destination'] = self.name
        if params.get('verbose', False):
            params['verbose'] = 2
        else:
            params['verbose'] = 0
        for key in ['enable', 'static', 'version', 'main', 'path']:
            try:
                del params[key]
            except KeyError:
                pass

        return params

    def _echo(self, msg, status=None):
        if status == 'ok':
            print(' '.join([msg, '\033[92m', 'OK' + '\033[0m']))
        elif status == 'fail':
            print(' '.join([msg, '\033[91m', 'FAIL' + '\033[0m']))
        else:
            print(msg)

    def _enable_client_extensions(self):
        directory = self.kwargs['static']
        for key, filename in list(self.extensions_map.items()):
            if filename in os.listdir(directory):
                self.cm.update(
                    key, {
                        "load_extensions": {
                            "{}/{}".format(self.name, filename[:-3]): True
                        }
                    }
                )

    def _enable_server_extensions(self):
        cfg = self.cm_server.get("jupyter_notebook_config")
        server_extensions = (
            cfg.setdefault("NotebookApp", {})
            .setdefault("server_extensions", [])
        )
        if "{}.nbextension".format(self.name) not in server_extensions:
            cfg["NotebookApp"]["server_extensions"] += ["{}.nbextension".format(self.name)]
        self.cm_server.update("jupyter_notebook_config", cfg)


def install_cmd(parser_args, setup_args):
    params = dict(list(setup_args.items()) + list(parser_args.__dict__.items()))
    name = params['name']
    del params['name']

    nb_setup = NBSetup(name, **params)
    nb_setup.install()
    if params['enable']:
        nb_setup.enable()


def remove_cmd(parser_args, setup_args):
    nb_setup = NBSetup(setup_args['name'], prefix=parser_args.prefix)
    nb_setup.disable()


def create_parser():
    parser = argparse.ArgumentParser(
        description="Install and uninstall nbextension")
    subparsers = parser.add_subparsers(title='subcommands')
    install_parser = subparsers.add_parser(
        "install",
        description="Install nbextension",
        help="Install nbextension"
    )
    install_parser.add_argument(
        "-e", "--enable",
        help="Automatically load server and nbextension on notebook launch",
        action="store_true"
    )

    default_kwargs = {'action': 'store', 'nargs': '?'}
    store_true_kwargs = {'action': 'store_true'}
    store_true = ["symlink", "overwrite", "quiet", "user"]
    install_kwargs = list(signature(install_nbextension).parameters)
    [
        install_parser.add_argument(
            "--{}".format(arg),
            **(store_true_kwargs if arg in store_true else default_kwargs)
        )
        for arg in install_kwargs
    ]

    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove an extension"
    )
    remove_parser.add_argument(
        "--prefix",
        action="store"
    )

    install_parser.set_defaults(main=install_cmd)
    remove_parser.set_defaults(main=remove_cmd)

    return parser


def find_static():
    static_path = os.path.join(os.getcwd(), 'static')
    if os.path.exists(static_path):
        return static_path
    else:
        raise StaticPathNotFound


def setup(**kwargs):
    parser = create_parser()
    args = parser.parse_args()
    args.main(args, kwargs)
