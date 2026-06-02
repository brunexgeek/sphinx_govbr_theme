#!/bin/bash

DIR=$(cd $(dirname "$0") && pwd)

SUDO_PREFIX=""
if docker ps 2>&1 | grep -q "/var/run/docker.sock"; then
    echo "Using 'sudo' to run Docker"
    SUDO_PREFIX="sudo"
fi

${SUDO_PREFIX} docker run -it --rm -v $DIR:/input -v $DIR/../sphinx_govbr_theme/static/css/:/output dart-sass:latest /input/styles.scss /output/styles-min.css