#!/bin/bash

CDIR="$(cd $(dirname $0) && pwd)"
docker build --rm -f "$CDIR/Dockerfile" -t sphinx:8.2.3-dev "$CDIR"
