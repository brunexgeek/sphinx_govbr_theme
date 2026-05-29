#!/bin/bash

DIR=$(cd $(dirname "$0") && pwd)
docker run -it --rm -v $DIR:/input -v $DIR/../sphinx_govbr_theme/static/css/:/output dart-sass:latest /input/styles.scss /output/styles.css