#!/bin/bash

cases='b2sum base32 base64 comm dir join ls md5sum expand ptx sha1sum sha256sum sha512sum shuf sort sum cat tsort uniq wc'

all_dir='../test_bins'

for c in $cases
do
    `rm -r $c`
    `mkdir $c`
    cmd="python rop_base.py $c 10 ./$c $all_dir/$c"
    echo $cmd
    eval $cmd
done

