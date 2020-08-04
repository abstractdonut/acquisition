mv release.keystore ../release.keystore

p4a apk

mv ../release.keystore release.keystore

zipalign -f -v 4 acquisition__arm64-v8a-release-unsigned-0.2.3-.apk acquisition__arm64-v8a-release-aligned-0.2.3-.apk

apksigner sign --ks release.keystore --ks-key-alias acquisition-keystore --out acquisition__arm64-v8a-release-signed-0.2.3-.apk acquisition__arm64-v8a-release-aligned-0.2.3-.apk

