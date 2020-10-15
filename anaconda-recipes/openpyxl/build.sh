#!/bin/bash

rm -f openpyxl.egg-info/.DS_Store
$PYTHON setup.py install --old-and-unmanageable
