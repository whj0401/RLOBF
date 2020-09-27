#!/bin/bash

binsdir='/dir/to/not/stripped/bins'
outdir='./explanation'

for b in sum dir wc comm base32 b2sum tsort ls uniq expand sort shuf cat ptx join sha1sum sha256sum sha512sum md5sum base64
do
    echo $b
    `sh ./get_distribution_data.sh $binsdir'/'$b $outdir`
done

