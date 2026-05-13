#!/bin/bash -x

SPHINXOPTS="-v -a --watch /opt/sphinx_govbr_theme/sphinx_govbr_theme"
SPHINX_COMMAND=sphinx-autobuild
SOURCEDIR=$(cd $(dirname $0) && pwd)
BUILDDIR=/docs-build

${SPHINX_COMMAND} ${SPHINXOPTS} "${SOURCEDIR}" "${BUILDDIR}"


