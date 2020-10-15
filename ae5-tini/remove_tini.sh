#!/bin/bash
for pod in workspace deploy; do
    if [ $pod == workspace ]; then
        istring=/ae-editor:
        var=ANACONDA_PLATFORM_IMAGES_EDITOR
    else
        istring=/ae-app:
        var=ANACONDA_PLATFORM_IMAGES_APP
    fi
    depl=deployment/anaconda-enterprise-ap-$pod
    env=$(kubectl set env $depl --list | grep ^$var=)
    echo $env
    current_image=$(echo $env | sed 's@^[^=]*=@@')
    img=$(echo $current_image | sed 's@-tini$@@')
    if [ "$current_image" != "$img" ]; then
        kubectl set env $depl $var=$img
        kubectl set env $depl --list | grep ^$var=
    else
        echo "$depl does not need to be updated"
    fi
done
