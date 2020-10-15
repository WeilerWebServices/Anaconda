#!/usr/bin/env python
# coding: utf-8

# Copyright (c) - Continuum Analytics

import argparse
import os
from os.path import exists, join
from pprint import pprint

from jupyter_core.paths import jupyter_config_dir

def install(enable=False, disable=False, prefix=None):
    """Install the nb_anaconda_theme config piece.

    Parameters
    ----------
    enable: bool
        Enable the nb_anaconda_theme on every notebook launch
    disable: bool
        Disable nb_anaconda_theme on every notebook launch
    """
    from notebook.services.config import ConfigManager

    if enable:
        if prefix is not None:
            path = join(prefix, "etc", "jupyter")
            if not exists(path):
                print("Making directory", path)
                os.makedirs(path)
        else:
            path = jupyter_config_dir()

        cm = ConfigManager(config_dir=path)
        print("Enabling nb_anaconda_theme in", cm.config_dir)
        cfg = cm.get("jupyter_notebook_config")
        print("Existing config...")
        pprint(cfg)

        extra_static_paths = (
            cfg.setdefault("NotebookApp", {})
            .setdefault("extra_static_paths", [])
        )

        if path not in extra_static_paths:
            cfg["NotebookApp"]["extra_static_paths"] += [path]

        extra_template_paths = (
            cfg.setdefault("NotebookApp", {})
            .setdefault("extra_template_paths", [])
        )

        theme_path = join(path, "custom", "templates")

        if theme_path not in extra_template_paths:
            cfg["NotebookApp"]["extra_template_paths"] += [theme_path]

        cm.update("jupyter_notebook_config", cfg)
        print("New config...")
        pprint(cm.get("jupyter_notebook_config"))

    if disable:
        if prefix is not None:
            path = join(prefix, "etc", "jupyter")
        else:
            path = jupyter_config_dir()

        cm = ConfigManager(config_dir=path)
        print("Disabling nb_anaconda_theme in", cm.config_dir)
        cfg = cm.get("jupyter_notebook_config")
        print("Existing config...")
        pprint(cfg)

        extra_static_paths = cfg["NotebookApp"]["extra_static_paths"]

        if path in extra_static_paths:
            cfg["NotebookApp"]["extra_static_paths"].remove(path)

        extra_template_paths = cfg["NotebookApp"]["extra_template_paths"]

        theme_path = join(path, "custom", "templates")

        if theme_path in extra_template_paths:
            cfg["NotebookApp"]["extra_template_paths"].remove(theme_path)

        cm.set("jupyter_notebook_config", cfg)
        print("New config...")
        pprint(cm.get("jupyter_notebook_config"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Installs nbextension")
    parser.add_argument(
        "-e", "--enable",
        help="Automatically load nb_anaconda_theme on notebook launch",
        action="store_true")
    parser.add_argument(
        "-d", "--disable",
        help="Remove nb_anaconda_theme from config on notebook launch",
        action="store_true")
    parser.add_argument(
        "-p", "--prefix",
        help="prefix where to load nb_anaconda_theme config",
        action="store")

    install(**parser.parse_args().__dict__)
