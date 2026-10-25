#!/bin/bash
# Decrypts the game's Lua scripts into work/lua (bytecode) and decompiles them into work/src.
# Needs unluac.jar (https://sourceforge.net/projects/unluac/) in work/ and Java (~/Android/jdk).
set -e
D=$(cd "$(dirname "$0")/../.." && pwd); W=$D/work
mkdir -p $W/apk $W/lua $W/src
unzip -q -o "$D/original/the_croods_1.3.1.apk" 'assets/*' -d $W/apk
python3 -I $D/tools/declua.py $W/apk/assets $W/lua
[ -f $W/unluac.jar ] || curl -L -o $W/unluac.jar https://sourceforge.net/projects/unluac/files/latest/download
J=${JAVA:-~/Android/jdk/bin/java}
cd $W/lua && find . -name '*.lua' | while read -r f; do
  mkdir -p "$W/src/$(dirname "$f")"; $J -jar $W/unluac.jar "$f" > "$W/src/$f" || echo "failed: $f"
done
echo "bytecode: $W/lua   decompiled: $W/src"
