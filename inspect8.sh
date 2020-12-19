[ -d inspect/v8a/ ] && rmdir inspect/v8a/
mkdir inspect
unzip acquisition__arm64-v8a-debug-0.2.1-.apk -d inspect/v8a/
mkdir inspect/v8a/assets/private
tar xf inspect/v8a/assets/private.mp3 -C inspect/v8a/assets/private/
chmod -R a+x inspect/v8a
