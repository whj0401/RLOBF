# -*- coding: utf-8 -*-

import os
import sys


size = 10
blocks = [0.1 * i for i in range(size + 1)]
counts = [0 for i in range(size)]


def compute_overhead_percentage(overheads):
    tmp = []
    for o in overheads[1:]:
        tmp.append(o / overheads[0])
    return tmp


#def compute_overhead_percentage(overheads):
#    return overheads


if __name__ == '__main__':
    d = sys.argv[1]
    files = os.listdir(d)
    files = sorted(files)
    avg_ohs = []
    for file in files:
        if '.json' in file:
            continue
        with open(os.path.join(d, file), 'r') as f:
            overheads = eval(f.read())
            overheads = compute_overhead_percentage(overheads)
            #overheads = list(filter(lambda o: o < 2.0, overheads))
            avg_oh = sum(overheads) / len(overheads) - 1.0
            #if avg_oh < 0:
            #    print(file, avg_oh, overheads)
            print(file, avg_oh)
            if avg_oh < 0:
                avg_oh = 0.0
            avg_ohs.append(avg_oh * 100)
            for idx in range(size):
                if blocks[idx] <= avg_oh < blocks[idx + 1]:
                    counts[idx] += 1
    print(blocks[1:])
    print(counts)
    print(avg_ohs)
    print('average overhead: %.2f' % (sum(avg_ohs) / len(avg_ohs)))
