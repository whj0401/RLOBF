# -*- coding: utf-8 -*-

import os

all_bins = ['expand', 'ls', 'ptx', 'sha1sum']


def get_overhead(fp):
    with open(fp) as f:
        ohs = eval(f.read())
        return (sum(ohs[1:]) / len(ohs[1:]) / ohs[0] - 1.0) * 100


#def table_perf():
#    print(' ' * 17 + ' 10      30      50      100')
#    perfs = ['10', '30', '50', '100']
#    for bin_name in all_bins:
#        files = [os.path.join(bin_name + '_perf', bin_name + '-' + p) for p in perfs]
#        ohs = [get_overhead(fp) for fp in files]
#        tmp_str = '\\texttt{%s}' % bin_name + ' ' * (8 - len(bin_name))
#        for oh in ohs:
#            tmp_str += ' & %2.1f ' % oh
#        tmp_str += '\\\\'
#        print(tmp_str)



def table_sim():
    print(' ' * 17 + ' 0.48    0.58    0.68    0.78    0.88')
    sims = ['0.48', '0.58', '0.68', '0.78', '0.88']
    for bin_name in all_bins:
        files = [os.path.join(bin_name + '_sim', bin_name + '-' + s) for s in sims]
        ohs = [get_overhead(fp) for fp in files]
        tmp_str = '\\texttt{%s}' % bin_name + ' ' * (8 - len(bin_name))
        for oh in ohs:
            tmp_str += ' & %2.1f ' % oh
        tmp_str += '\\\\'
        print(tmp_str)


if __name__ == '__main__':
#    table_perf()
#    print()
    table_sim()
