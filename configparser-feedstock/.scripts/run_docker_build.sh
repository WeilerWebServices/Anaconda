#!/usr/bin/env bash

# PLEASE NOTE: This script has been automatically generated by conda-smithy. Any changes here
# will be lost next time ``conda smithy rerender`` is run. If you would like to make permanent
# changes to this script, consider a proposal to conda-smithy so that other feedstocks can also
# benefit from the improvement.

set -xeo pipefail

THISDIR="$( cd "$( dirname "$0" )" >/dev/null && pwd )"
PROVIDER_DIR="$(basename $THISDIR)"

FEEDSTOCK_ROOT=$(cd "$(dirname "$0")/.."; pwd;)
RECIPE_ROOT="${FEEDSTOCK_ROOT}/recipe"

docker info

# In order for the conda-build process in the container to write to the mounted
# volumes, we need to run with the same id as the host machine, which is
# normally the owner of the mounted volumes, or at least has write permission
export HOST_USER_ID=$(id -u)
# Check if docker-machine is being used (normally on OSX) and get the uid from
# the VM
if hash docker-machine 2> /dev/null && docker-machine active > /dev/null; then
    export HOST_USER_ID=$(docker-machine ssh $(docker-machine active) id -u)
fi

ARTIFACTS="$FEEDSTOCK_ROOT/build_artifacts"

if [ -z "$CONFIG" ]; then
    set +x
    FILES=`ls .ci_support/linux_*`
    CONFIGS=""
    for file in $FILES; do
        CONFIGS="${CONFIGS}'${file:12:-5}' or ";
    done
    echo "Need to set CONFIG env variable. Value can be one of ${CONFIGS:0:-4}"
    exit 1
fi

if [ -z "${DOCKER_IMAGE}" ]; then
    SHYAML_INSTALLED="$(shyaml -h || echo NO)"
    if [ "${SHYAML_INSTALLED}" == "NO" ]; then
        echo "WARNING: DOCKER_IMAGE variable not set and shyaml not installed. Falling back to condaforge/linux-anvil-comp7"
        DOCKER_IMAGE="condaforge/linux-anvil-comp7"
    else
        DOCKER_IMAGE="$(cat "${FEEDSTOCK_ROOT}/.ci_support/${CONFIG}.yaml" | shyaml get-value docker_image.0 condaforge/linux-anvil-comp7 )"
    fi
fi

mkdir -p "$ARTIFACTS"
DONE_CANARY="$ARTIFACTS/conda-forge-build-done-${CONFIG}"
rm -f "$DONE_CANARY"

if [ -z "${CI}" ]; then
    DOCKER_RUN_ARGS="-it "
fi

export UPLOAD_PACKAGES="${UPLOAD_PACKAGES:-True}"
docker run ${DOCKER_RUN_ARGS} \
           -v "${RECIPE_ROOT}":/home/conda/recipe_root:ro,z \
           -v "${FEEDSTOCK_ROOT}":/home/conda/feedstock_root:rw,z \
           -e CONFIG \
           -e BINSTAR_TOKEN \
           -e HOST_USER_ID \
           -e UPLOAD_PACKAGES \
           -e GIT_BRANCH \
           -e UPLOAD_ON_BRANCH \
           -e CI \
           $DOCKER_IMAGE \
           bash \
           /home/conda/feedstock_root/${PROVIDER_DIR}/build_steps.sh

# verify that the end of the script was reached
test -f "$DONE_CANARY"