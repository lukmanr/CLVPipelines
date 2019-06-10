#!/bin/bash

KFCTL_VER=v0.5.1
KFCTL_PLATFORM=linux
KFCTL_TAR=kfctl_${KFCTL_VER}_${KFCTL_PLATFORM}.tar.gz
KFCTL_PATH=https://github.com/kubeflow/kubeflow/releases/download/${KFCTL_VER}/${KFCTL_TAR}

if [[ $# < 6 ]]; then
    echo "Error: Arguments missing. [install INSTALL_PATH PROJECT_ID CLIENT_ID CLIENT_SECRET ZONE KFAPP]"
    exit 1
fi

echo "Installing KFCTL to: "${1}
echo "Using PROJECT_ID to: "${2}
echo "Installing KFAPP to: "${6}
echo "Creating GKE in zone: "${5}

export PROJECT=${2}
export CLIENT_ID=${3}
export CLIENT_SECRET=${4}
export ZONE=${5}
export KFAPP=${6}

if [ -d ${1} ]; then
    echo "Error: Install folder already exists. Remove it and restart installation."
    exit 1
fi

mkdir ${1}
cd ${1}

curl -O -L  ${KFCTL_PATH}
tar -xvf ${KFCTL_TAR}
chmod 755 kfctl

./kfctl init ${KFAPP} --platform gcp --project ${PROJECT}
cd ${KFAPP}
../kfctl generate all -V --zone ${ZONE}

echo "Starting deployment ...."
../kfctl apply all -V