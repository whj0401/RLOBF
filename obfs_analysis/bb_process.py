import sys, os

bb_c = 0
preds_c = 0
succs_c = 0
identify_bb = False


def help(l):
    global bb_c
    global preds_c
    global succs_c
    global identify_bb
    items = l.split()

    #if items[0].startswith('4') or items[0].startswith('2') or items[0].startswith('6'):
    if "[" in l:
        identify_bb = True
                #bb_c = bb_c + 1
    if "PRED:" in l:
        preds_c = preds_c + 1
        if identify_bb == True:
            bb_c = bb_c + 1
            identify_bb = False
    if "SUCC:" in l:
        succs_c = succs_c + 1
        if identify_bb == True:
            bb_c = bb_c + 1
            identify_bb = False


if __name__ == '__main__':
    # read output file of blklist.py
    path = sys.argv[1]
    with open(path, 'r') as f:
        lines = f.readlines()
        for l in lines:
            help(l)
        node_num = bb_c
        edge_num = (preds_c + succs_c) / 2
        print("edge : " + str(edge_num))
        print("node : " + str(node_num))


