#!/bin/bash
if [ -z "$1" ]
then
    exit 1
fi
`objdump -d --prefix-addresses  $1 | grep -v Disassembly | grep -v -e '(bad)' | awk '{print $3}' | sort | uniq -c | python $(dirname $0)/stealth_classify.py $2`

