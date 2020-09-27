#!/bin/bash

bin=$1
outdir=$2'/'`basename $bin`'_ops_info'

dump='/tmp/'`basename $bin`'.s'
op_data=$outdir'/op_distribution'

`objdump -D -j .text $bin > $dump`
`python3 extract_func_opcodes_from_objdump.py $dump $outdir`
`python3 count_opcodes.py $outdir $op_data`

