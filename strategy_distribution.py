import os

font = {'size': 20}

DATA_S = [
    '\n',
    'rewards',
    'cycles',
    'actions',
    'iteration',
    'similarity'
]

gamma = 1.0


def get_rewards_files(outdir, name, num):
    files = [os.path.join(outdir, 'train/env/train_%d/reward_records_%s_train_env_%d.txt' % (i + 1, name, i + 1)) for i
             in range(num)]
    return files


def read_rewards(file_path: str):
    rewards = []
    similaritys = []
    task_clocks_increase = []
    iterations = []
    ac_traces = []
    LDS = len(DATA_S)
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i in range(int(len(lines) / len(DATA_S))):
            for s in range(len(DATA_S)):
                assert lines[i * LDS + s].startswith(DATA_S[s])
                if s == 1:
                    rl = eval(lines[i * LDS + s].split(':')[1])
                    if rl[-1] == -10.0:
                        break
                    r = 0.0
                    # r = rl[-1]
                    for v in reversed(rl):
                        r = gamma * r + v
                    rewards.append(float(r))
                elif s == 2:
                    tc = eval(lines[i * LDS + s].split(':')[1])
                    assert len(tc) > 1, 'the first element should be the original binary'
                    task_clocks_increase.append(tc[-1] / tc[0])
                elif s == 3:
                    ac_trace = eval(lines[i * LDS + s].split(':')[1])
                    ac_traces.append(ac_trace)
                    iterations.append(len(ac_trace))
                # elif s == 4:
                # here is the iteration number, but I have gotten it from the len of action trace
                elif s == 5:
                    sim = float(lines[i * LDS + s].split(':')[1])
                    similaritys.append(sim)
    return rewards, task_clocks_increase, ac_traces, iterations, similaritys


def count_distribution(ac_traces):
    counter = {}
    for i in range(10):
        counter[str(i)] = 0

    for trace in ac_traces:
        for a in trace:
            counter[a] += 1
    # nop:0 bb:124, func:56 instr:78
    precise_dis = [0 for _ in range(10)]
    rough_dis = {'nop': 0, 'bb': 0, 'func': 0, 'instr': 0}
    for i in range(10):
        precise_dis[i] = counter[str(i)]

    for i in range(10):
        if i == 0:
            rough_dis['nop'] += counter[str(i)]
        elif i in range(1, 5):
            rough_dis['bb'] += counter[str(i)]
        elif i in range(5, 7) or i == 9:
            rough_dis['func'] += counter[str(i)]
        else:
            rough_dis['instr'] += counter[str(i)]

    return precise_dis, rough_dis


if __name__ == '__main__':
    bin_paths = {
        'uniq': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.4-1-uniq', 6),
        'expand': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.4-1-expand', 6),
        'sum': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.7-1-sum', 6),
        'ptx': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.2-1-ptx', 6),
        'cat': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.3-1-cat', 6),
        'sha512sum': ('/home/hwangdz/export-d1/rl-select-div-out-keras-8.31-1-sha512sum', 6),
        'md5sum': ('/home/hwangdz/export-d1/rl-select-div-out-keras-8.28-2-md5sum', 6),
        'sha1sum': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.12-10-sha1sum', 6),
        'ls': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.5-1-ls/', 6),
        'sort': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.3-1-sort/', 6),
        'b2sum': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.6-1-b2sum/', 6),
        'base64': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.11-1-base64/', 6),
        'comm': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.6-1-comm/', 6),
        'join': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.1-1-join/', 6),
        'wc': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.6-1-wc/', 6),
        'base32': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.6-1-base32/', 6),
        'dir': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.7-1-dir/', 6),
        'sha256sum': ('/home/hwangdz/export-d1/rl-select-div-out-keras-8.30-1-sha256sum/', 6),
        'shuf': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.3-1-shuf/', 6),
        'tsort': ('/home/hwangdz/export-d1/rl-select-div-out-keras-9.5-1-tsort/', 6),
    }
    files = []
    for name, outdir in bin_paths.items():
        files.extend(get_rewards_files(outdir[0], name, outdir[1]))
    total_precise = [0 for _ in range(10)]
    total_rough = {'nop': 0, 'bb': 0, 'func': 0, 'instr': 0}
    for f in files:
        _, _, ac_traces, _, _ = read_rewards(f)
        tmp_precise, tmp_rough = count_distribution(ac_traces[len(ac_traces) - 20:])
        for i in range(10):
            total_precise[i] += tmp_precise[i]
        for k in total_rough.keys():
            total_rough[k] += tmp_rough[k]
    print(total_precise)
    print(total_rough)
