#!/bin/bash
# Installs (without sudo) JDK 21, Android SDK command-line tools, the emulator and an
# Android 9 x86 image into ~/Android, then creates the Croods_API28 virtual device.
# Running it means accepting the Android SDK license: https://developer.android.com/studio/terms
set -e
mkdir -p ~/Android/Sdk/cmdline-tools ~/Android/jdk
cd ~/Android
if [ ! -x jdk/bin/java ]; then
  curl -L -o jdk.tar.gz "https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse"
  tar -xzf jdk.tar.gz -C jdk --strip-components=1 && rm jdk.tar.gz
fi
if [ ! -x Sdk/cmdline-tools/latest/bin/sdkmanager ]; then
  curl -L -o clt.zip https://dl.google.com/android/repository/commandlinetools-linux-16111833_latest.zip
  unzip -q -o clt.zip -d Sdk/cmdline-tools && rm -rf Sdk/cmdline-tools/latest
  mv Sdk/cmdline-tools/cmdline-tools Sdk/cmdline-tools/latest && rm clt.zip
fi
export JAVA_HOME=~/Android/jdk ANDROID_HOME=~/Android/Sdk
SM=$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager
yes | $SM --licenses >/dev/null
$SM --install "platform-tools" "emulator" "build-tools;35.0.0" "system-images;android-28;default;x86"
echo no | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd -n Croods_API28 \
  -k "system-images;android-28;default;x86" -d pixel_2 --force
C=~/.android/avd/Croods_API28.avd/config.ini
sed -i -e 's/^hw.keyboard=.*/hw.keyboard=yes/' -e 's/^hw.ramSize=.*/hw.ramSize=2048/' \
       -e 's/^hw.gpu.enabled=.*/hw.gpu.enabled=yes/' -e 's/^hw.gpu.mode=.*/hw.gpu.mode=swiftshader_indirect/' $C
echo "Done. Start the emulator with:  ~/Android/Sdk/emulator/emulator -avd Croods_API28 -gpu swiftshader_indirect"
