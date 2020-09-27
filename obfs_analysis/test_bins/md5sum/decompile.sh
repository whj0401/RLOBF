#!/bin/bash

ida='/d/IDA_Pro_v7.0_Portable/ida'
decompile_py='/d/rl-obfs/ida-batch_decompile-master/ida_batch_decompile.py'
# prefix='/d/rl-obfs/rl-select-div-last-10'
name=$1

eval "rm *.*"
eval "rm -r save_*"

cmd="$ida -A -S\"$decompile_py --output=.\" \"$name\""
echo $cmd
eval $cmd

for i in 1 2 3 4 5 6 7 8 9 10
do
    cmd="$ida -A -S\"$decompile_py --output=.\" \"obfs_$i\""
    echo $cmd
    eval $cmd
done
