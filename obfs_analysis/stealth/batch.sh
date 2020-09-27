#!/bin/bash

all='b2sum base32 base64 comm dir join ls md5sum expand ptx sha1sum sha256sum sha512sum shuf sort sum cat tsort uniq wc'

dir='../test_bins'

for c in $all
do
    `rm -r $c`
    `mkdir $c`
    # original binary
    `sh ./stealth_instdist.sh $dir/$c/$c ./$c/orig.json`
    # obfs
    for idx in 1 2 3 4 5 6 7 8 9 10
    do
        `sh ./stealth_instdist.sh $dir/$c/obfs_$idx ./$c/obfs_$idx.json`
    done
    # create figures
    `python3 ./fig6.py ./$c $c.pdf $c`
done

