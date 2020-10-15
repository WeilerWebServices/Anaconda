#!/bin/bash
set -e
if [ ! -f tini ]; then
    echo "tini must be downloaded first."
    echo "please run download_tini.sh or download manually."
    exit 1
fi
chmod +x tini
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
    current_image=$(echo $env | sed 's@^[^=]*=@@')
    img=$(echo $current_image | sed 's@-tini$@@')
    echo "Building tini add-on for $img"
    sed -i "s@^FROM .*@FROM $img@" Dockerfile
    docker build -t $img-tini .
    docker push $img-tini
    echo $env
    if [ "$current_image" == "$img" ]; then
        kubectl set env $depl $var=$img-tini
        kubectl set env $depl --list | grep ^$var=
    else
        echo "$depl does not need to be updated"
    fi
done

