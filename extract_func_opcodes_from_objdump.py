# -*- coding: utf-8 -*-

import re
import sys
import os

func_name_re = re.compile('<[_a-zA-Z].*>:')
hex_re = re.compile('{[0-9a-fA-F], 2}:')


def is_end_of_func(line):
    return line == '\n'


def instrs_to_opcodes(instrs):
    opcodes = ''
    for instr in instrs:
        opcode = instr.split('\t')
        if len(opcode) < 3:
            continue
        opcode = opcode[-1].split()[0]
        if opcode == '(bad)' or opcode == '...':
            continue
        opcodes += opcode + ' '
    return opcodes


if __name__ == '__main__':
    file_name = sys.argv[1]
    outdir = sys.argv[2]
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    with open(file_name, 'r') as f:
        lines = f.readlines()
        in_func = False
        func_name = None
        func_instrs = []
        for l in lines:
            search = func_name_re.search(l)
            if not in_func and search:
                in_func = True
                func_name = search[0][:-1]
                func_instrs = []
            elif in_func:
                if is_end_of_func(l):
                    in_func = False
                    opcodes = instrs_to_opcodes(func_instrs)
                    with open(os.path.join(outdir, func_name), 'w') as f:
                        f.write(opcodes)
                else:
                    func_instrs.append(l)


