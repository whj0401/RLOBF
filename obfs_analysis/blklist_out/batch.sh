#!/bin/bash

all='b2sum base32 base64 comm dir join ls md5sum expand ptx sha1sum sha256sum sha512sum shuf sort sum cat tsort uniq wc'
dir='../test_bins'

ida='/home/hwangdz/idaedu-7.3/idat64'

for bin in $all
do
    bin_path=$dir"/$bin/$bin"
    `sudo rm -rf $bin`
    `mkdir $bin`
    echo $bin_path
    cmd="$ida -A -S\"../blklist.py $bin/orig.txt\" $bin_path"
    eval $cmd
    # obfs 1 - 10
    for i in 1 2 3 4 5 6 7 8 9 10
    do
        bin_path=$dir"/$bin/obfs_$i"
        cmd="$ida -A -S\"../blklist.py $bin/obfs_$i.txt\" $bin_path"
        eval $cmd
    done
done

