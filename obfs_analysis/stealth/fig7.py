# -*- coding: utf-8 -*-
import sys
import os
import copy
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
matplotlib.use('Agg')
font = {'size': 10}
matplotlib.rc('font', **font)

def load_distribution_json(path):
    with open(path, 'r') as f:
        d = json.load(f)
        return d


def get_plot_data(ticks, data: dict):
    tmp = []
    for t in ticks:
        tmp.append(data[t])
    return tuple(tmp)


def draw_distribution(orig_json, obfs_jsons, fig_path, title):
    orig_data = load_distribution_json(orig_json)
    obfs_datas = [load_distribution_json(tmp) for tmp in obfs_jsons]
    optypes = orig_data['ratio'].keys()
    optypes = tuple(optypes)

    plt.title(title)

    handles = []
    x = list(i for i in range(1, len(optypes) + 1))
    plt.xticks(x, labels=optypes, rotation=-90)

    x = list(i-0.1 for i in range(1, len(optypes) + 1))
    line1, = plt.plot(x, get_plot_data(optypes, orig_data['ratio']), 'bo', label='Original')
    handles.append(line1)

    position = 1.1
    for op in optypes:
        tmp = []
        for obfs in obfs_datas:
            tmp.append(obfs['ratio'][op])
        line2, = plt.plot([position]*len(tmp), tmp, marker='.',linestyle='--',color='r', label='Avg Obfs')
        position += 1
    handles.append(line2)

    plt.yscale('log')
    plt.ylabel('Percentage of Instructions (Log Scale)')

    plt.legend(handles=handles, loc='upper left')

    plt.savefig(fig_path)


def get_all_json_paths(dir_path):
    cases = 'b2sum base32 base64 comm dir join ls md5sum expand ptx sha1sum sha256sum sha512sum shuf sort sum cat tsort uniq wc'.split()
    all_paths = {}
    for c in cases:
        all_paths[c] = {}
        all_paths[c]['orig'] = os.path.join(dir_path, c+'/orig.json')
        all_paths[c]['obfs'] = [os.path.join(dir_path, c+'/obfs_%d.json' % idx) for idx in range(1, 11)]
    return all_paths


def draw_distribution_all(all_paths: dict):
    orig_datas = []
    for bin_name in all_paths.keys():
        orig_datas.append(load_distribution_json(all_paths[bin_name]['orig']))
    optypes = orig_datas[0]['ratio'].keys()
    x = tuple(list(i for i in range(1, len(optypes) + 1)))

    orig_all_data = []
    for op in optypes:
        tmp = []
        for d in orig_datas:
            tmp.append(d['ratio'][op])
        orig_all_data.append(tmp)
    plt.boxplot(orig_all_data,
                showmeans=False,
                showfliers=False,
                labels=['original'] * 26)

    # avg distribution of all obfs exe
    avg_obfs_all_data = []
    for op in optypes:
        tmp =  []
        for bin_name in all_paths.keys():
            for obfs_json_path in all_paths[bin_name]['obfs']:
                d = load_distribution_json(obfs_json_path)
                tmp.append(d['ratio'][op])
        avg_obfs_all_data.append(sum(tmp) / len(tmp))
    plt.plot(x, avg_obfs_all_data, 'r.', )

    plt.xticks(x, labels=optypes, rotation=-90)
    plt.yscale('log')
    plt.ylabel('Percentage of Instructions (Log Scale)')

    black_line = mlines.Line2D([], [], color='black', label='Original')
    red_line = mlines.Line2D([], [], color='red', label='Avg Obfs')
    plt.legend(handles=[black_line, red_line], loc='upper left')

    plt.savefig('all.pdf')


def draw_distribution_all2(all_paths):
    plt.clf()
    orig_datas = []
    for bin_name in all_paths.keys():
        orig_datas.append(load_distribution_json(all_paths[bin_name]['orig']))
        optypes = orig_datas[0]['ratio'].keys()
    x = tuple(list(i for i in range(1, len(optypes) + 1)))
    handles = []
    position = 0.9
    for op in optypes:
        tmp = []
        for d in orig_datas:
            tmp.append(d['ratio'][op])
        line1, = plt.plot([position, position], [min(tmp), max(tmp)], marker='o',linestyle='-',color='b', label='Original')
        position += 1
        if len(handles) == 0:
            handles.append(line1)

    position = 1.1
    for op in optypes:
        tmp =  []
        for bin_name in all_paths.keys():
            for obfs_json_path in all_paths[bin_name]['obfs']:
                d = load_distribution_json(obfs_json_path)
                tmp.append(d['ratio'][op])
        line2, = plt.plot([position]*len(tmp), tmp, marker='.',linestyle='--',color='r', label='Avg Obfs')
        position += 1
        if len(handles) == 1:
            handles.append(line2)

    plt.xticks(x, labels=optypes, rotation=-90)
    plt.yscale('log')
    plt.ylabel('Percentage of Instructions (Log Scale)')
    plt.legend(handles=handles, loc='upper left')
    plt.savefig('all2.pdf')



def draw_a_bin():
    data_dir = sys.argv[1]
    output_file = sys.argv[2]
    title = sys.argv[3]
    orig_json = os.path.join(data_dir, 'orig.json')
    obfs_jsons = [os.path.join(data_dir, 'obfs_%d.json' % idx) for idx in range(1, 11)]
    draw_distribution(orig_json, obfs_jsons, output_file, title)


if __name__ == '__main__':
    all_paths = get_all_json_paths('.')
    #draw_distribution_all(all_paths)
    draw_distribution_all2(all_paths)
    #draw_a_bin()



