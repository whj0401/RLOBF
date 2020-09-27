# -*- coding: utf-8 -*-
import os


def read_rop_base_res(path):
    with open(path, 'r') as f:
        lines = f.readlines()
        eliminate_ratios = []
        for l in lines:
            eliminate_ratios.append(float(l))
        return sum(eliminate_ratios) / len(eliminate_ratios)


def batch():
    d = '.'
    cases = 'b2sum base32 base64 comm dir join ls md5sum expand ptx sha1sum sha256sum sha512sum shuf sort sum cat tsort uniq wc'.split()
    cases = sorted(cases)
    res = {}
    for c in cases:
        res[c] = read_rop_base_res(os.path.join(d, c + '/rop_base.res'))
    return res


if __name__ == '__main__':
    res = batch()
    count = 0
    avg_eli = 0.0
    table3 = ''
    for item in res.items():
        avg_eli += item[1]
        if count % 2 == 0:
            table3 += '\\texttt{%s} & %.1f & ' % item
        else:
            table3 += '\\texttt{%s} & %.1f \\\\\n' % item
        count += 1
    print(table3)
    print('Average elimination ratio: %.1f' % (avg_eli / len(res.keys())))

