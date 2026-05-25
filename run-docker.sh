#!/bin/bash

set -e

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
POD_THEME_PATH=/opt/sphinx_govbr_theme
SPHINX_IMAGE=sphinx:8.2.3-dev
PROJECT_DIR="$1"

if [ "$1" == "--container" ]; then
    cd $POD_THEME_PATH
    pip install -e .
    cd /docs
    sphinx-autobuild -v -a --watch /opt/sphinx_govbr_theme/sphinx_govbr_theme /docs /docs-build
    exit 0
fi

if [[ ! "$PROJECT_DIR" || ! -d "$PROJECT_DIR" ]]; then
    echo "No project directory specified, using example"
    PROJECT_DIR="$BASE_DIR/example"
fi

WORK_DIR=`mktemp -d -p /tmp`
if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
    echo "Could not create temporary directory"
    exit 1
fi

echo "Running $SPHINX_IMAGE"
echo " Documentation: $PROJECT_DIR"
echo "Work directory: $WORK_DIR"

docker run -it --rm \
    -v $PROJECT_DIR:/docs \
    -v $WORK_DIR:/docs-build \
    -v $BASE_DIR:$POD_THEME_PATH \
    -e DOCS_BUILD=$WORK_DIR \
    -p 8000:8000 \
    --network host \
    --name govbr-sphinx \
    $SPHINX_IMAGE $POD_THEME_PATH/run-docker.sh --container
