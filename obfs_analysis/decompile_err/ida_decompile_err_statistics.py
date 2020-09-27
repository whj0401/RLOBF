# -*- coding: utf-8 -*-

import os
import re


def get_errs(fp):
    errs = dict()
    with open(fp, 'r') as f:
        lines = f.readlines()
        for l in lines[:-1]:
            if l.startswith('#error'):
                err_str = l.split(':')[1]
                err_str = err_str.split('(')[0]
                if err_str in errs:
                    errs[err_str] += 1
                else:
                    errs[err_str] = 1
    return errs


def merge(d1, d2):
    for k in d2.keys():
        if k in d1:
            d1[k] += d2[k]
        else:
            d1[k] = d2[k]


decompile_dir = '../test_bins'


obfs_all_errs = dict()
orig_all_errs = dict()

os.system('find %s -name "*.c" > all_c' % decompile_dir)

with open(os.path.join('all_c')) as f:
    fps = f.readlines()
    for fp in fps:
        fp = os.path.join(decompile_dir, fp[:-1])
        tmp = get_errs(fp)
        base_name = os.path.basename(fp)
        if base_name.startswith('obfs'):
            merge(obfs_all_errs, tmp)
        else:
            merge(orig_all_errs, tmp)


print('obfs')
for k, v in obfs_all_errs.items():
    print('%s : %d' % (k, v))
print('orig')
for k, v in orig_all_errs.items():
    print('%s : %d' % (k, v))
