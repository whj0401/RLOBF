# -*- coding: utf-8 -*-

import os

bin_names = 'md5sum, sha512sum, comm, uniq, nl, b2sum, sum, wc, sha256sum, ptx, sha1sum, join, dir, shuf, tail, tsort, ls, sort, base64, base32'
bin_names = bin_names.split(', ')


total_opcodes = 0
num_valid_funcs = 0

for name in bin_names:
    op_dir = './%s_ops_info/' % name
    html_dir = './%s_html' % name
    all_func_ops_files = os.listdir(op_dir)
    for func_f in all_func_ops_files:
        if not func_f.startswith('<'):
            continue
        print('file: ' + op_dir + func_f)
        with open(op_dir + func_f, 'r') as f:
            opcodes = f.read()
            if len(opcodes) < 20:
                continue
            num_valid_funcs += 1
            total_opcodes += len(opcodes.split())

print('total opcodes' + str(total_opcodes))
print('functions: ' + str(num_valid_funcs))
print('avg per function: ' + str(total_opcodes / num_valid_funcs))


