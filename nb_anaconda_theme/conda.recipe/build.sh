#!/bin/bash
$PYTHON setup.py install

# set dir references
MAIN_DIR=$RECIPE_DIR/..

# custom content into $PREFIX/etc/jupyter/custom
mkdir -p                     $PREFIX/etc/jupyter/custom
cp -rf $MAIN_DIR/custom/*    $PREFIX/etc/jupyter/custom
