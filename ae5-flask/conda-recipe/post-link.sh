#!/bin/bash

# A couple of simple tests to make sure we are in an AE5 deployment
echo "--------------------------" >> $PREFIX/.messages.txt
echo "ae5-flask post-link script" >> $PREFIX/.messages.txt
echo "--------------------------" >> $PREFIX/.messages.txt
if [[ "$APP_HOST$APP_ID" != "" ]]; then
    echo "In a deployment; no changes applied" >> $PREFIX/.messages.txt
elif [[ "$TOOL_HOST" == "" ]]; then
    echo "Not in a session; no changes applied" >> $PREFIX/.messages.txt
else
    echo "PREFIX: $PREFIX" >> $PREFIX/.messages.txt
    for fname in $PREFIX/lib/python*/site-packages/flask/helpers.py; do
        if ! grep -q ae5-flask $fname; then
            cat >> $fname <<EOT

# begin ae5-flask patch
_old_url_for = url_for
def url_for(endpoint, **values):
    return '/proxy/8086' + _old_url_for(endpoint, **values)
# end ae5-flask patch
EOT
            echo "$fname: patched for AE5 sessions"  >> $PREFIX/.messages.txt
        else
            echo "$fname: already patched"  >> $PREFIX/.messages.txt
        fi
    done
    for fname in $PREFIX/lib/python*/site-packages/werkzeug/serving.py; do
        if ! grep -q ae5-flask $fname; then
            sed -E -i 's@^(\s*)(def log_startup.*)@\1\2\n'\
'\1    # begin ae5-flask patch\n'\
'\1    _log("info", " * Proxied on https://%s/proxy/%d/",\n'\
'\1         os.environ["TOOL_HOST"], sock.getsockname()[1])\n'\
'\1    # end ae5-flask patch@' $fname
            echo "Patched $fname"  >> $PREFIX/.messages.txt
            echo "$fname: patched for AE5 sessions"  >> $PREFIX/.messages.txt
        else
            echo "$fname: already patched"  >> $PREFIX/.messages.txt
        fi
    done
fi
echo "--------------------------" >> $PREFIX/.messages.txt
