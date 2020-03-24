mogrify -resize 100x100 *.png

convert *.png \
    -background transparent \
    -scale 80x80  \
    -gravity SouthEast  \
    -extent 100x100 \
    -set filename:fname '%t-f' +adjoin '%[filename:fname].png' 

convert *.png \
    -background transparent \
    -scale 80x80  \
    -gravity NorthWest  \
    -extent 100x100 \
    -set filename:fname '%t-b' +adjoin '%[filename:fname].png'

rm *f-b.png
