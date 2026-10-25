#!/bin/bash
# Runs the game logic on the desktop (see README). Needs work/ from decompile.sh and
# lupa installed into work/pylib:  python3 -m pip install --target work/pylib lupa
D=$(cd "$(dirname "$0")/../.." && pwd)
BYTECODE_DIR=$D/work/lua LUPA_PATH=$D/work/pylib python3 -I $D/tools/harness.py $D/work/src $D/server/assets "$@" \
  2>&1 | grep -v '^\[game\]'
