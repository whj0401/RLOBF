import sys, os
import json

def count_node_edge(path):
    # read output file of blklist.py
    node_num = 0
    preds_c = 0
    succs_c = 0
    identify_bb = False
    func_num = 0

    with open(path, 'r') as f:
        lines = f.readlines()
        for l in lines:
            items = l.split()
            if l.startswith('#########'):
                func_num += 1
                continue
            if '[' in l:
                identify_bb = True
            if "PRED:" in l:
                preds_c += 1
                if identify_bb:
                    node_num += 1
                    identify_bb = False
            if "SUCC:" in l:
                succs_c += 1
                if identify_bb:
                    node_num += 1
                    identify_bb = False
    assert node_num > 0, path
    assert preds_c > 0, path
    assert succs_c > 0, path
    return node_num, (preds_c + succs_c) / 2, func_num


def get_node_edge_statistics(bin_dir):
    # the dir saves blklist.py outputs of original bin, and 10 obfs bins
    num_obfs = 10
    orig_path = os.path.join(bin_dir, 'orig.txt')
    obfs_paths = [os.path.join(bin_dir, 'obfs_%d.txt' % idx) for idx in range(1, 1 + num_obfs)]
    orig_data = count_node_edge(orig_path)
    obfs_data = [count_node_edge(path) for path in obfs_paths]
    avg_obfs_node = 0.0
    avg_obfs_edge = 0.0
    avg_obfs_func = 0.0
    for d in obfs_data:
        avg_obfs_node += d[0]
        avg_obfs_edge += d[1]
        avg_obfs_func += d[2]
    avg_obfs_node = avg_obfs_node / num_obfs
    avg_obfs_edge = avg_obfs_edge / num_obfs
    avg_obfs_func = avg_obfs_func / num_obfs
    # node, avg_obfs_node, rising ratio
    node_res = (orig_data[0], avg_obfs_node, (avg_obfs_node / orig_data[0] - 1.0) * 100)
    # edge, avg_obfs_edge, rising ratio
    edge_res = (orig_data[1], avg_obfs_edge, (avg_obfs_edge / orig_data[1] - 1.0) * 100)
    func_res = (orig_data[2], avg_obfs_func, (avg_obfs_func / orig_data[2] - 1.0) * 100)
    return node_res, edge_res, func_res


def get_knot_count(path: str):
    # the output file of idaout
    with open(path, 'r') as f:
        lines = f.readlines()
        knot_count = 0
        is_first_func = True
        label_addr = {}
        jmp_addr = {}

        for i in range(0, len(lines)):
            l = lines[i]
            items = l.split()
            if len(items) > 0:
                if "global" in items[0]:
                    if is_first_func:
                        # take record
                        is_first_func = False
                    else:
                        jmp_addr_num = {}
                        for k, v in jmp_addr.items():
                            v1 = v+":"
                            if v1 in label_addr:
                                 # let it crash if inter-procedure jmp occurs
                                addr = label_addr[v1]
                                jmp_addr_num[k] = addr

                        for k1, v1 in jmp_addr_num.items():
                            for k2, v2 in jmp_addr_num.items():
                                if k1 < k2 and k2 < v1 and v1 < v2:  # situation 1
                                    knot_count = knot_count + 1
                                if k2 < k1 and k1 < v2 and v2 < v1:  # situation 2
                                    knot_count = knot_count + 1
                        label_addr = {}
                        jmp_addr = {}
                if len(items) == 1 and "loc_" in items[0]:
                    # identify a new label
                    nl = lines[i+1]
                    addr = nl.split()[0]  # let it crash if wrong
                    label_addr[items[0]] = addr
                if len(items) == 3 and items[1].startswith('j'):
                    des = items[2]
                    source = items[0]
                    jmp_addr[source] = des
        return knot_count / 2


def get_knot_statistics(bin_dir):
    # dir of idaout files, including orig.txt obfs_1.txt - obfs.10.txt
    num_obfs = 10
    orig_knot = get_knot_count(os.path.join(bin_dir, 'orig.txt'))
    obfs_knots = [get_knot_count(os.path.join(bin_dir, 'obfs_%d.txt' % idx)) for idx in range(1, 1 + num_obfs)]
    avg_obfs_knot = sum(obfs_knots) / num_obfs
    return orig_knot, avg_obfs_knot, (avg_obfs_knot / orig_knot - 1.0) * 100


def get_cyclomatic_complexity(nodes, edges):
    return edges - nodes + 2


def get_cyclomatic_statistics(node_data, edge_data):
    orig_nodes, avg_obfs_nodes, _ = node_data
    orig_edges, avg_obfs_edges, _ = edge_data
    orig_cc = get_cyclomatic_complexity(orig_nodes, orig_edges)
    avg_obfs_cc = get_cyclomatic_complexity(avg_obfs_nodes, avg_obfs_edges)
    return orig_cc, avg_obfs_cc, (avg_obfs_cc / orig_cc - 1.0) * 100


def get_norefs_instructions(bin_dir):
    num_obfs = 10
    orig_path = os.path.join(bin_dir, 'orig.txt')
    obfs_paths = [os.path.join(bin_dir, 'obfs_%d.txt' % idx) for idx in range(1, 1 + num_obfs)]
    orig_n = 0
    obfs_ns = []
    with open(orig_path) as f:
        orig_n = int(f.read())
    for p in obfs_paths:
        with open(p) as f:
            obfs_ns.append(int(f.read()))
    obfs_n = sum(obfs_ns) / len(obfs_ns)
    return orig_n, obfs_n, (obfs_n / orig_n - 1.0) * 100


decompilation_dir = '/home/hwangdz/export-d1/rl-select-decompilation'

def get_err_num(decompilation_output):
    with open(decompilation_output) as f:
        lines = f.readlines()
        assert lines[-1].startswith('#error "There were ')
        tmp = lines[-1].split()
        return int(tmp[3])


def get_decompilation_err(bin_dir):
    num_obfs = 10
    bin_name = os.path.basename(bin_dir)
    orig_path = os.path.join(bin_dir, bin_name + '.c')
    obfs_paths = [os.path.join(bin_dir, 'obfs_%d.c' % idx) for idx in range(1, 1 + num_obfs)]
    orig_n = get_err_num(orig_path)
    obfs_ns = []
    for p in obfs_paths:
        obfs_ns.append(get_err_num(p))
    obfs_n = sum(obfs_ns) / len(obfs_ns)
    return orig_n, obfs_n, (obfs_n / orig_n - 1.0) * 100


def get_table2_row(blklist_path, idaout_path):
    bin_name = os.path.basename(blklist_path)
    node_data, edge_data, func_data = get_node_edge_statistics(blklist_path)
    knot_data = get_knot_statistics(idaout_path)
    cc_data = get_cyclomatic_statistics(node_data, edge_data)
    norefs_data = get_norefs_instructions(bin_name)
    derr_data = get_decompilation_err(os.path.join(decompilation_dir, bin_name))
    #return node_data, edge_data, knot_data, cc_data
    return node_data, edge_data, cc_data, func_data, norefs_data, derr_data
    # print('# of basic blocks: %d\t%.2f\t%.3f' % node_data)
    # print('# of CFG edges   : %d\t%.2f\t%.3f' % edge_data)
    # print('Knot Count       : %d\t%.2f\t%.3f' % knot_data)
    # print('Cyclomatic Num   : %d\t%.2f\t%.3f' % cc_data)


def get_all_data_from(blklist_out_dir, idaout_dir):
    table = dict()
    for bin_name in os.listdir(blklist_out_dir):
        if not os.path.isdir(os.path.join(blklist_out_dir, bin_name)):
            continue
        table[bin_name] = get_table2_row(os.path.join(blklist_out_dir, bin_name), os.path.join(idaout_dir, bin_name))
    return table


size = 3 * 6

def latex_table2(t: dict):
    avg_item = [0.0 for _ in range(size)]
    count = 0
    # sort all bins by name
    t = list(t.items())
    t = sorted(t, key=lambda bc: bc[0])
    for bin_name, content in t:
        tmp = [bin_name + ' ' * (10 - len(bin_name))]
        count += 1
        for c in content:
            tmp.extend(c)
        for idx in range(1, size + 1):
            avg_item[idx - 1] += tmp[idx]
        #print('\\texttt{%s} & %d & %d & %.1f & %d & %d & %.1f & %d & %d & %.1f & %d & %d & %.1f \\\\' % tuple(tmp))
        # do not use knot data
        tmp = tmp[:10]
        print('\\texttt{%s} & %d & %.1f & %.1f & %d & %.1f & %.1f & %d & %.1f & %.1f \\\\' % tuple(tmp))
    for idx in range(size):
        avg_item[idx] /= count
    #print('\\hline\n\\textbf{average}    & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\' % tuple(avg_item))
    avg_item = avg_item[:9]
    print('\\hline\n\\textbf{average} & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\' % tuple(avg_item))


def latex_table_func_data(t: dict):
    avg_item = [0.0 for _ in range(size)]
    count = 0
    t = list(t.items())
    t = sorted(t, key=lambda bc: bc[0])
    for bin_name, content in t:
        tmp = [bin_name + ' ' * (10 - len(bin_name))]
        count += 1
        for c in content:
            tmp.extend(c)
        for idx in range(1, size + 1):
            avg_item[idx - 1] += tmp[idx]
        tmp = tmp[:1] + tmp[10:]
        print('\\texttt{%s} & %d & %.1f & %.1f & %d & %.1f & %.1f & %d & %.1f & %.1f \\\\' % tuple(tmp))
    for idx in range(size):
        avg_item[idx] /= count
    avg_item = avg_item[9:]
    print('\\hline\n\\textbf{average} & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\' % tuple(avg_item))


if __name__ == '__main__':
    table2 = get_all_data_from('../blklist_out', '../idaout_txt')
    with open('table2.json', 'w') as f:
        json.dump(table2, f, indent=2)
    with open('table2.json', 'r') as f:
        table2 = json.load(f)
        latex_table2(table2)
        print()
        latex_table_func_data(table2)


