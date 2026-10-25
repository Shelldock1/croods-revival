#!/bin/bash
# Rebuild and sign croods_offline.apk from the original APK.
set -e
D=$(cd "$(dirname "$0")/.." && pwd)
ORIG="${1:-$D/original/the_croods_1.3.1.apk}"
BT=~/Android/Sdk/build-tools/35.0.0
export JAVA_HOME=~/Android/jdk PATH=~/Android/jdk/bin:$PATH
TMP=$(mktemp -d)
python3 -I "$D/tools/patch_apk.py" "$ORIG" "$TMP/unsigned.apk"
$BT/zipalign -f -p 4 "$TMP/unsigned.apk" "$TMP/aligned.apk"
$BT/apksigner sign --ks "$D/debug.keystore" --ks-pass pass:android --out "$D/croods_offline.apk" "$TMP/aligned.apk"
rm -rf "$TMP"
echo "built $D/croods_offline.apk"
