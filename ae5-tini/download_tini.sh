#!/bin/sh
set -e
TINI_VERSION=v0.19.0
TINI_BASE=https://github.com/krallin/tini/releases/download
TINI_KEY=595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7
if ! curl -OL ${TINI_BASE}/${TINI_VERSION}/tini; then
    echo "tini could not be downloaded."
    exit 1
fi
chmod +x tini
if ! gpg --batch --keyserver ha.pool.sks-keyservers.net --recv-keys $TINI_KEY; then
    echo "tini was downloaded but the verification key could not be obtained."
    echo "if the keyserver receive failed, a retry often works."
    echo "if you trust the download you can proceed with the image build."
    rm -rf ~/.gnupg
    exit 1
fi
curl -OL ${TINI_BASE}/${TINI_VERSION}/tini.asc
if gpg --batch --verify tini.asc tini; then
    echo "tini has been downloaded and verified"
    rm -rf tini.asc ~/.gnupg
else
    rm -rf tini.asc ~/.gnupg tini
    exit 1
fi
