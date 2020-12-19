rm -rf inspect/v7a/
mkdir inspect/v7a
unzip acquisition__armeabi-v7a-debug-0.2.1-.apk -d inspect/v7a/
mkdir inspect/v7a/assets/private
tar xf inspect/v7a/assets/private.mp3 -C inspect/v7a/assets/private/
chmod -R a+x inspect/v7a
