mv keystore/release.keystore release.keystore
p4a clean_all

# v7a release
#------------
mv specs/armeabi-v7a-release/.p4a .p4a
p4a apk
zipalign -f -v 4 acquisition__armeabi-v7a-release-unsigned-0.2.4-.apk acquisition__armeabi-v7a-release-aligned-0.2.4-.apk
apksigner sign --ks release.keystore --ks-key-alias acquisition-key --out acquisition__armeabi-v7a-release-signed-0.2.4-.apk acquisition__armeabi-v7a-release-aligned-0.2.4-.apk
mv .p4a specs/armeabi-v7a-release/.p4a

# v7a debug
#----------

mv specs/armeabi-v7a-debug/.p4a .p4a
p4a apk
mv .p4a specs/armeabi-v7a-debug/.p4a

p4a clean_all

# v8a release
#------------
mv specs/arm64-v8a-release/.p4a .p4a
p4a apk
zipalign -f -v 4 acquisition__arm64-v8a-release-unsigned-0.2.4-.apk acquisition__arm64-v8a-release-aligned-0.2.4-.apk
apksigner sign --ks release.keystore --ks-key-alias acquisition-key --out acquisition__arm64-v8a-release-signed-0.2.4-.apk acquisition__arm64-v8a-release-aligned-0.2.4-.apk
mv .p4a specs/arm64-v8a-release/.p4a

# v8a debug
#----------
mv specs/arm64-v8a-debug/.p4a .p4a
p4a apk
mv .p4a specs/arm64-v8a-debug/.p4a

mv release.keystore keystore/release.keystore























