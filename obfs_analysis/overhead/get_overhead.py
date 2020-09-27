import os
import json
from subprocess import Popen, DEVNULL, PIPE


def run_cmd_with_perf_stat(cmd: list, stat_file_path, repeat=1, stdout_file=None):
    # need root to run
    #perf_stat = ['/usr/bin/perf', 'stat', '-e', 'task-clock',
    #             '--repeat', str(repeat), '-o', stat_file_path]
    perf_stat = ['/usr/bin/chrt', '-f', '99', '/usr/bin/perf', 'stat',
                 '-e', 'task-clock', '--repeat', str(repeat), '-o', stat_file_path]
    print(' '.join(cmd))
    if stdout_file is None:
        stdout_file = DEVNULL
    p = Popen(perf_stat + cmd, stdout=stdout_file, stderr=PIPE)
    return p


def get_perf_stat_result(stat_file_path: str):
    with open(stat_file_path, 'r') as sf:
        lines = sf.readlines()
        for line in lines:
            es = line.strip().split()
            if len(es) >= 2 and 'task-clock' in line:
                es[0] = es[0].replace(',', '')
                return float(es[0])
    raise Exception('cannot find task-clock value in file: %s' % stat_file_path)



# the parameters for testing the output binaries, and the original running cost
# to run all these binaries at the same time makes the time result inaccurate
train_bin_dict = {
    'sha1sum': (['../../dir4test/a'], None),
    'sha256sum': (['../../dir4test/a'], None),
    'b2sum': (['../../dir4test/a-t'], None),
    'md5sum': (['../../dir4test/a'], None),
    'sha512sum': (['../../dir4test/a-t'], None),
    'ls': (['-lRa', '/dir/for/test/ls'], None),
    'sort': (['../../dir4test/test-sort.txt'], None),
    'tsort': (['../../dir4test/test-sort.txt'], None),
    'shuf': (['../../dir4test/test-shuf.txt'], None),
    'sum': (['../../dir4test/a-t10M'], None),
    'uniq': (['../../dir4test/test-shuf.txt'], None),
    'join': (['../../dir4test/test-sort.txt', '../../dir4test/test-shuf.txt'], None),
    'comm': (['../../dir4test/test-comm1.txt', '../../dir4test/test-comm2.txt'], None),
    'cat': (['../../dir4test/a', '../../dir4test/a-t10M'], None),
    'wc': (['../../dir4test/test-shuf.txt'], None),
    'ptx': (['../../dir4test/test-ptx.txt'], None),
    'expand': (['-t', '2', '../../dir4test/test-expand.txt'], None),
    'base64': (['../../dir4test/opengl32sw.dll'], None),
    'base32': (['../../dir4test/a-t5M'], None),
    'dir': (['-lRa', '/dir/for/test/ls'], None),
}


bin_dir = '../test_bins'


def test_a_bin(bin_name, dir):
    repeat = 100
    bin_names = [bin_name]
    bin_names.extend(['obfs_%d' % i for i in range(1, 11)])
    # the first is the original binary
    idx = 0
    overheads = []
    for name in bin_names:
        p = os.path.join(dir, bin_name, name)
        cmd = [p] + train_bin_dict[bin_name][0]
        tmp_out = 'tmpout%d' % idx
        stat_p = 'stat%d' % idx
        with open(tmp_out, 'w') as tmp_out_f:
            subp = run_cmd_with_perf_stat(cmd, stat_p, repeat, tmp_out_f)
            subp.wait()
        tmp_clock = get_perf_stat_result(stat_p)
        if name == bin_name and train_bin_dict[bin_name][1] is not None:
            overheads.append(train_bin_dict[bin_name][1])
        else:
            overheads.append(tmp_clock)
            # record the time
            if name == bin_name:
                train_bin_dict[bin_name] = (train_bin_dict[bin_name][0], tmp_clock)
        if name == bin_name:
            print(tmp_clock)
        if idx > 0:
            if bin_name == 'cat':
                tmp_ret = os.system('diff tmpout0 tmpout%d > /dev/null' % idx)
                #assert tmp_ret == 0, "%s %d" % (bin_name, idx)
                if tmp_ret != 0:
                    overheads.pop()
            else:
                with open('tmpout0') as orig_out:
                    with open('tmpout%d' % idx) as obfs_out:
                        if bin_name == 'shuf':
                            orig_txt = orig_out.readlines()
                            obfs_txt = obfs_out.readlines()
                            orig_txt = ','.join(list(sorted(orig_txt)))
                            obfs_txt = ','.join(list(sorted(obfs_txt)))
                            #assert orig_txt == obfs_txt, "%s %d" % (bin_name, idx)
                            if orig_txt != obfs_txt:
                                overheads.pop()
                        else:
                            orig_txt = orig_out.read()
                            obfs_txt = obfs_out.read()
                            #assert orig_txt == obfs_txt, "%s %d" % (bin_name, idx)
                            if orig_txt != obfs_txt:
                                overheads.pop()
        idx += 1
    return overheads


def a_batch(bin_dir, output_dir):
    res = dict()
    for bin_name in train_bin_dict.keys():
        oh = test_a_bin(bin_name, bin_dir)
        res[bin_name] = oh
        with open(output_dir + bin_name, 'w') as f:
            f.write(str(oh))
    with open(output_dir + 'overhead.json', 'w') as f:
        json.dump(res, f, indent=2)
    os.system('rm -f stat*')
    os.system('rm -f tmpout*')


if __name__ == '__main__':
    a_batch(bin_dir, 'overhead_output/')


