# -*- coding: utf-8 -*-

from idaapi import *
from idautils import *
from idc import *


def get_text_section():
    ts = get_segm_by_name('.text')
    return (ts.start_ea, ts.end_ea)


def get_noref_bbs(function):
    """ Return list of basic block address tuples that do not have any predecessor blocks for given
    function. """
    all_bbs = set()
    referenced_bbs = set()
    flowchart = FlowChart(function)
    for bb in flowchart:
        # get start and end for all basic blocks in function
        all_bbs.add((bb.startEA, bb.endEA))
        # get start and end for function start basic block
        if bb.startEA == function.startEA:
            referenced_bbs.add((bb.startEA, bb.endEA))
        # get start and end for all basic blocks that have a predecessor
        for succ in bb.succs():
            referenced_bbs.add((succ.startEA, succ.endEA))
    return all_bbs - referenced_bbs


def count_insn_num(start_ea, end_ea):
    num = 0
    for h in Heads(start_ea, end_ea):
        num += 1
    return num


def count_insn_not_in_func():
    insn_not_in_func = 0
    #targets = []
    text_start, text_end = get_text_section()
    with open('text_range', 'w') as tf:
        tf.write(str((text_start, text_end)))
    ip = text_start
    insn_str = GetDisasm(ip)
    while ip < text_end:
        ip += 1
        tmp_str = GetDisasm(ip)
        if tmp_str == insn_str:
            # the ip does not move to next instruction, add 1 repeatedly
            continue
        tmp_func = get_func(ip)
        if tmp_func is None:
            if not (tmp_str.startswith('align ') or tmp_str.startswith('db ') or tmp_str.startswith('dd ')):
                insn_not_in_func += 1
                #targets.append(ip)
        else:
            ip = max(tmp_func.end_ea - 1, ip)
            # some function may have basic blocks having no reference, we count instructions of these blocks
            #noref_bbs = get_noref_bbs(tmp_func)
            #for bb in noref_bbs:
            #    insn_not_in_func += count_insn_num(bb[0], bb[1])
        insn_str = tmp_str
    return insn_not_in_func


if __name__ == '__main__':
    n = count_insn_not_in_func()
    with open('insn_not_in_func.txt', 'w') as f:
        f.write("%d\n" % n)
        #for ea in all_eas:
        #    f.write("%x\n" % ea)
    exit()

