#!/bin/bash
GULPFILE="../../gulpfile.js"
if [[ -e $GULPFILE ]]; then
  echo -e "gulpfile already exists, skipping"
  exit 1
fi

echo "require('continuum-gulp').registerAllTasks();" > $GULPFILE
