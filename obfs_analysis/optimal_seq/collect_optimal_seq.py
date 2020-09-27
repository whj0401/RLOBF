# -*- coding: utf-8 -*-

import os

gamma = 1.0


def get_final_rwd(rewards):
    #return rewards[-1]
    if gamma == 1.0:
        return sum(rewards)
    tr = 0.0
    for r in reversed(rewards):
        tr = tr * gamma + r
    return tr

def read_rewards(path):
    res = []
    with open(path) as f:
        lines = f.readlines()
        n = (len(lines) + 2) // 6
        for i in range(50, n):
            offset = 6 * i
            rewards = eval(lines[offset + 1][12:])
            actions = eval(lines[offset + 3][12:])
            r = get_final_rwd(rewards)
            res.append((r, actions, i + 1))
    #res = list(sorted(res, key=lambda i: i[0], reverse=True))
    return res


action_map = {
    '0': 'NOP',
    '1': 'OPA',
    '2': 'BBR',
    '3': 'BFI',
    '4': 'BBS',
    '5': 'CFA',
    '6': 'FR',
    '7': 'GRA',
    '8': 'IR',
    '9': 'FIL',
}


def acts2seq(acts: list):
    tmp = []
    for a in acts:
        if a == '0':
            continue
        tmp.append('\\texttt{%s}' % action_map[a])
    return ','.join(tmp)



all_dirs = {
    # add or change this dictionary to get optimal sequences
    'md5sum': '../../output',
}


def table_row(bname, seqs):
    head = '\multirow{3}{*}{\\texttt{%s}}    ' % bname
    res = head
    res += ' & ' + acts2seq(seqs[0]) + ' \\\\\n' + ' ' * len(head)
    res += ' & ' + acts2seq(seqs[1]) + ' \\\\\n' + ' ' * len(head)
    res += ' & ' + acts2seq(seqs[2]) + ' \\\\\n'
    res += '\hline'
    return res


if __name__ == '__main__':
    seq_lens = []
    last_seq_lens = []
    optimal_dict = dict()
    for b, d in all_dirs.items():
        all_tests_log = []
        optimal_dict[b] = []
        tmp_last_seq_lens = []
        for idx in range(1, d[1] + 1):
            rwd_log_p = os.path.join(d[0], 'train', 'env', 'train_%d' % idx, 'reward_records_%s_train_env_%d.txt' % (b.split('-')[0], idx))
            tmp = read_rewards(rwd_log_p)
            all_tests_log.extend(tmp)
            tmp_last_seq_lens.append(len(tmp[-1][1]))
        last_seq_lens.append(sum(tmp_last_seq_lens) / len(tmp_last_seq_lens))
        print(b)
        all_tests_log = list(sorted(all_tests_log, key=lambda i: i[0], reverse=True))
        for i in range(3):
            print(all_tests_log[i])
            optimal_dict[b].append(all_tests_log[i][1])
        print()
        seq_lens.append(len(all_tests_log[0][1]))


    blocks = [i * 2 for i in range(10)]
    counts = [0 for _ in range(15)]
    for l in seq_lens:
        counts[l//2] += 1
    print(counts)
    print(last_seq_lens)
    print('average sequence length: %.2f' % (sum(last_seq_lens) / len(last_seq_lens)))

    print()

    for b in sorted(optimal_dict.keys()):
        print(table_row(b, optimal_dict[b]))
