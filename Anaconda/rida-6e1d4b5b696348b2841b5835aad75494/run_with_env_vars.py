#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

for key in os.environ:
    if key.startswith("INTEGRATION_TEST"):
        print(key, " : ", os.environ[key])
