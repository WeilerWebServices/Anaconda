#!/bin/bash

SRC_DIR=$RECIPE_DIR/..
cd $SRC_DIR

npm --loglevel warn install -g 

# Make nodejs app environment-safe -- remove /usr/bin/env line
pushd $PREFIX
mv lib/node_modules/tty.js/bin/tty.js lib/node_modules/tty.js/bin/tty.js.old
echo "#!${PREFIX}/bin/node" >  lib/node_modules/tty.js/bin/tty.js
tail -n +2 lib/node_modules/tty.js/bin/tty.js.old >> lib/node_modules/tty.js/bin/tty.js
chmod +x lib/node_modules/tty.js/bin/tty.js
popd


POST_LINK=$PREFIX/bin/.${PKG_NAME}-post-link.sh
cp $RECIPE_DIR/post-link.sh $POST_LINK
chmod +x $POST_LINK

mkdir -p $PREFIX/etc/wakari/apps
cp $RECIPE_DIR/terminal.json $PREFIX/etc/wakari/apps/terminal.json

