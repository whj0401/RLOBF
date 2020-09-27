# -*- coding: utf-8 -*-

import sys
import os
import json

head_count = 8


def read_headline(f):
    count = 0
    headline_info = []
    while count < head_count:
        line = f.readline().strip()
        if line.startswith('(probability'):
            count += 1
            tmp_info = line.split('<b>')
            headline_info.append((count-1, float(tmp_info[1].split('<')[0]), float(tmp_info[2].split('<')[0])))
    return headline_info


def read_a_table(f):
    while True:
        line = f.readline().strip()
        if line == '<tbody>':
            break

    table_info = []

    while True:
        line = f.readline().strip()
        if line.startswith('<td'):
            line = f.readline().strip()
            contribution = float(line)
            line = f.readline()
            line = f.readline()
            line = f.readline().strip()
            token = line
            table_info.append((contribution, token))
        elif line == '</tbody>':
            break
    return table_info

def read_num_of_opcodes(f):
    while f:
        line = f.readline()
        if len(line) == 0:
            return 1
        line = line.strip()
        if line.startswith('num of opcodes:'):
            num = int(line.split(':')[-1])
            return num
    return 1



def read_a_html_explanation(file_path):
    #print('read %s' % file_path)
    with open(file_path, 'r') as f:
        headline_info = read_headline(f)
        table_info = []
        for _ in range(head_count):
            table_info.append(read_a_table(f))
        num_ops = read_num_of_opcodes(f)
    return headline_info, table_info, num_ops


def read_files(files):
    heads = []
    tables = []
    num_ops = []
    for fp in files:
        head, table, num = read_a_html_explanation(fp)
        heads.append(head)
        tables.append(table)
        num_ops.append(num)
    return heads, tables, num_ops


def is_control_token(token):
    if 'j' in token or 'call' in token or 'ret' in token or 'test' in token or 'cmp' in token:
        return True
    return False

def is_stack_token(token):
    if 'push' in token or 'pop' in token or 'leave' in token:
        return True
    return False

def is_mov_token(token):
    if token.startswith('mov'):
        return True
    return False

def is_others(token):
    return not is_control_token(token) and not is_stack_token(token) and not is_mov_token(token)

def count_control_opcodes(files, top_valid=5):
    heads, tables, num_ops = read_files(files)
    data = []
    for i in range(head_count):
        i_data = {'ctl_occ':0, 'ctl_occ_weighted': 0,
                  'stack_occ': 0, 'stack_occ_weighted': 0,
                  'mov_occ': 0, 'mov_occ_weighted': 0,
                  'other_occ': 0, 'other_occ_weighted': 0,
                  'total_ops':0}
        for f_idx in range(len(files)):
            valid = tables[f_idx][i][:top_valid]
            for item in valid:
                contribution, token = item
                # to compute the proportion of control opcodes in top 5
                if is_control_token(token):
                    i_data['ctl_occ'] += 1
                    i_data['ctl_occ_weighted'] += num_ops[f_idx]
                if is_stack_token(token):
                    i_data['stack_occ'] += 1
                    i_data['stack_occ_weighted'] += num_ops[f_idx]
                if is_mov_token(token):
                    i_data['mov_occ'] += 1
                    i_data['mov_occ_weighted'] += num_ops[f_idx]
                if is_others(token):
                    i_data['other_occ'] += 1
                    i_data['other_occ_weighted'] += num_ops[f_idx]
            i_data['total_ops'] += num_ops[f_idx]
        i_data['ctl_proportion_weighted'] = i_data['ctl_occ_weighted'] / i_data['total_ops'] / top_valid
        i_data['ctl_proportion'] = i_data['ctl_occ'] / len(files) / top_valid
        i_data['stack_proportion_weighted'] = i_data['stack_occ_weighted'] / i_data['total_ops'] / top_valid
        i_data['stack_proportion'] = i_data['stack_occ'] / len(files) / top_valid
        i_data['mov_proportion_weighted'] = i_data['mov_occ_weighted'] / i_data['total_ops'] / top_valid
        i_data['mov_proportion'] = i_data['mov_occ'] / len(files) / top_valid
        i_data['other_proportion_weighted'] = i_data['other_occ_weighted'] / i_data['total_ops'] / top_valid
        i_data['other_proportion'] = i_data['other_occ'] / len(files) / top_valid
        data.append(i_data)
    return data


if __name__ == '__main__':
    html_dir = sys.argv[1]
    files = os.listdir(html_dir)
    files.remove('ctl_proportion_data')
    files.remove('ctl_proportion_data_with_toc')
    for i in range(len(files)):
        files[i] = os.path.join(html_dir, files[i])
    data = count_control_opcodes(files)
    with open(os.path.join(html_dir, 'ctl_proportion_data'), 'w') as f:
        json.dump(data, f, indent=2)



