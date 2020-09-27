# -*- coding: utf-8 -*-

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('Agg')
font = {'size': 16}
matplotlib.rc('font', **font)


def read_json(fp):
    with open(fp, 'r') as f:
        return json.load(f)


def draw_data(op_dis_fps, ex_dis_fps):
    op_keys = ['control', 'stack_op', 'mov', 'others']
    op_dis_s = [read_json(op_dis_fp)[0] for op_dis_fp in op_dis_fps]
    op_dis = {'control': 0, 'stack_op': 0, 'mov': 0, 'others': 0}
    for bin_info in op_dis_s:
        for k in op_keys:
            op_dis[k] += bin_info[k]
    total = sum([v for _, v in op_dis.items()])
    op_dis['control_proportion'] = op_dis['control'] / total
    op_dis['stack_op_proportion'] = op_dis['stack_op'] / total
    op_dis['mov_proportion'] = op_dis['mov'] / total
    op_dis['others_proportion'] = op_dis['others'] / total

    original = (
        op_dis['control_proportion'], op_dis['stack_op_proportion'], op_dis['mov_proportion'],
        op_dis['others_proportion'])

    ex_dis_s = [read_json(ex_dis_fp) for ex_dis_fp in ex_dis_fps]
    weighted_keys = ['ctl_occ_weighted', 'stack_occ_weighted', 'mov_occ_weighted', 'other_occ_weighted']
    unw_keys = ['ctl_occ', 'stack_occ', 'mov_occ', 'other_occ']
    ex_dis = [
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0},
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0},
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0},
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0},
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0},
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0},
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0},
        {'ctl_occ': 0, 'stack_occ': 0, 'mov_occ': 0, 'other_occ': 0, 'ctl_occ_weighted': 0, 'stack_occ_weighted': 0,
         'mov_occ_weighted': 0, 'other_occ_weighted': 0}
    ]
    for i in range(8):
        for k in weighted_keys:
            ex_dis[i][k] = sum([dis[i][k] for dis in ex_dis_s])
        for k in unw_keys:
            ex_dis[i][k] = sum([dis[i][k] for dis in ex_dis_s])
        ex_dis[i]['total_ops'] = sum([dis[i]['total_ops'] for dis in ex_dis_s])
    weighted_total = 0
    for k in weighted_keys:
        weighted_total += ex_dis[0]['total_ops']

    for ex_strategy in ex_dis:
        ex_strategy['ctl_proportion_weighted'] = ex_strategy['ctl_occ_weighted'] / ex_strategy['total_ops'] / 5.0
        ex_strategy['stack_proportion_weighted'] = ex_strategy['stack_occ_weighted'] / ex_strategy['total_ops'] / 5.0
        ex_strategy['mov_proportion_weighted'] = ex_strategy['mov_occ_weighted'] / ex_strategy['total_ops'] / 5.0
        ex_strategy['other_proportion_weighted'] = ex_strategy['other_occ_weighted'] / ex_strategy['total_ops'] / 5.0

    weighted_ex = [
        (ex_strategy['ctl_proportion_weighted'], ex_strategy['stack_proportion_weighted'],
         ex_strategy['mov_proportion_weighted'], ex_strategy['other_proportion_weighted']) for ex_strategy in ex_dis
    ]
    # unweighted_ex = [
    #     (ex_strategy['ctl_proportion'], ex_strategy['stack_proportion'], ex_strategy['mov_proportion'],
    #      ex_strategy['other_proportion']) for ex_strategy in ex_dis
    # ]

    x = np.arange(4)

    width = 0.1
    plt.tight_layout()

    # plt.xlabel('opcode type')
    # plt.xticks(x, labels=('control', 'stack', 'mov', 'others'))
    # # plt.title('distribution and contribution')
    #
    # plt.bar(x, original, width=width, label='original', lw=1)
    # count = 1
    # for e in unweighted_ex:
    #     plt.bar(x + count * width, e, width=width, label='s%d' % (count - 1), lw=1)
    #     count += 1
    # plt.legend(loc="upper left")
    # plt.savefig('unweighted.pdf')

    plt.clf()
    # plt.xlabel('opcode type')
    plt.xticks(x, labels=('control transfer', 'stack access', 'register assignment', 'others'))
    # plt.title('distribution and contribution')
    plt.bar(x, original, width=width, label='original', lw=1)
    count = 1
    for e in weighted_ex:
        plt.bar(x + count * width, e, width=width, label='s%d top-5' % (count - 1), lw=1)
        count += 1
    plt.legend(loc='upper left')
    plt.savefig('weighted.pdf')

    num_strategies = len(weighted_ex)
    width = 0.3

    plt.clf()
    # plt.xlabel('opcode type')
    avg_x = x + width / 2
    avg_x[0] += 0.3
    avg_x[1] += 0.3
    avg_x[2] += 0.6
    avg_x[3] += 0.15
    plt.xticks(avg_x, labels=('control transfer', 'stack access', 'register assignment', 'others'), rotation=-8)
    # plt.title('distribution and top-5 proportion')
    plt.bar(x, original, width=width, label='original', lw=1)
    avg_weighted_e = [0.0, 0.0, 0.0, 0.0]
    for e in weighted_ex:
        avg_weighted_e[0] += e[0]
        avg_weighted_e[1] += e[1]
        avg_weighted_e[2] += e[2]
        avg_weighted_e[3] += e[3]
    avg_weighted_e[0] /= num_strategies
    avg_weighted_e[1] /= num_strategies
    avg_weighted_e[2] /= num_strategies
    avg_weighted_e[3] /= num_strategies
    plt.bar(x + width, avg_weighted_e, width=width, label='top-5', lw=1)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig('avg_weighted.pdf')


if __name__ == '__main__':
    bin_names = ['b2sum', 'base32', 'base64', 'comm', 'dir', 'join', 'ls', 'md5sum',
                 'nl', 'ptx', 'sha1sum', 'sha256sum', 'sha512sum', 'shuf', 'sort', 'sum',
                 'tail', 'tsort', 'uniq', 'wc']
    ori_fps = ['explanation/' + name + '_ops_info/op_distribution' for name in bin_names]
    ex_fps = ['explanation/' + name + '_html/ctl_proportion_data' for name in bin_names]
    save_name = 'explanation/global'

    draw_data(ori_fps, ex_fps)

