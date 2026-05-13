#!/bin/bash

BDIR=$(cd $(dirname $0) && pwd)

find $BDIR -type f -name "*.po" | while read -r INPUT; do
    OUTPUT="${INPUT%.po}.mo"
    echo "Compiling '$INPUT'"
    msgfmt $INPUT -o $OUTPUT
done
