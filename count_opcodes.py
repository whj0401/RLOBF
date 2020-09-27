# -*- coding: utf-8 -*-

import os
import sys
import json


def count_opcodes_from_file(file_path):
    with open(file_path, 'r') as f:
        opcodes = f.read().split()
        counter = dict()
        for op in opcodes:
            if op in counter:
                counter[op] += 1
            else:
                counter[op] = 1
        return counter


def count_from_files(files):
    counter = dict()
    for file in files:
        tmp_counter = count_opcodes_from_file(file)
        for op, count in tmp_counter.items():
            if op in counter:
                counter[op] += count
            else:
                counter[op] = count
    return counter


def op_classifier(op_str):
    if 'j' in op_str or 'call' in op_str or 'ret' in op_str or 'cmp' in op_str or 'test' in op_str:
        return 'control'
    elif op_str.startswith('push') or op_str.startswith('pop') or op_str.startswith('leave'):
        return 'stack_op'
    elif op_str.startswith('mov'):
        return 'mov'
    else:
        return 'others'


def print_statistics(d):
    s = {
        'control':0, 'stack_op':0, 'mov':0, 'others':0
    }
    total = 0
    for op_str, num in d.items():
        s[op_classifier(op_str)] += num
        total += num
    tmp = {}
    for k in s.keys():
        tmp[k+'_proportion'] = s[k]/total
        print(k + ': %d (%f)' % (s[k], s[k]/total))
    s.update(tmp)
    return s


if __name__ == '__main__':
    directory = sys.argv[1]
    output = sys.argv[2]
    if os.path.isdir(directory):
        file_names = os.listdir(directory)
        if 'op_distribution' in file_names:
            file_names.remove('op_distribution')
        if 'op_distribution_with_toc' in file_names:
            file_names.remove('op_distribution_with_toc')
        for i in range(len(file_names)):
            file_names[i] = os.path.join(directory, file_names[i])
        counter = count_from_files(file_names)
    elif os.path.isfile(directory):
        file_name = directory
        counter = count_opcodes_from_file(file_name)
    else:
        counter = dict()
    data = print_statistics(counter)
    with open(output, 'w') as of:
        json.dump([data, counter], of, indent=2)


