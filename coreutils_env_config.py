# -*- coding: utf-8 -*-
import os
import sys
# use this file to create all environments for trainning and evaluating by coreutils

# the parameters for testing the output binaries, and the original running cost
# to run all these binaries at the same time makes the time result inaccurate
train_bin_dict = {
    'sha1sum': (['./dir4test/a'], None),
    'sha256sum': (['./dir4test/a-t'], None),
    'b2sum': (['./dir4test/a-t'], None),
    'md5sum': (['./dir4test/a'], None),
    'sha512sum': (['./dir4test/a-t'], None),
    'ls': (['-lRa', 'dir/for/test'], None),
    'sort': (['./dir4test/test-sort.txt'], None),
    'tsort': (['./dir4test/test-sort.txt'], None),
    'shuf': (['./dir4test/test-shuf.txt'], None),
    'sum': (['./dir4test/a-t10M'], None),
    'uniq': (['./dir4test/test-shuf.txt'], None),
    'join': (['./dir4test/test-sort.txt', './dir4test/test-shuf.txt'], None),
    'nl': (['./dir4test/test-shuf.txt'], None),
    'comm': (['./dir4test/test-comm1.txt', './dir4test/test-comm2.txt'], None),
    'cat': (['./dir4test/a', './dir4test/a-t10M'], None),
    'wc': (['./dir4test/test-shuf.txt'], None),
    'ptx': (['./dir4test/test-ptx.txt'], None),
    'expand': (['-t', '2', './dir4test/test-expand.txt'], None),
    'base64': (['./dir4test/a'], None),
    'base32': (['./dir4test/a-t5M'], None),
    'dir': (['-lRa', 'dir/for/test'], None),
}

# you should have all bins here
src_coreutils_path = './samples'

# directory for all trainning, evaluating
# save it to a ssd
output_dir = './output'

src_uroboros = './uroboros-diversification'

gym_head_lines = """from src.coreutils_gym_env import *

iteration_num = 20
test_times=5"""

def create_an_env(test_id,
                  exe_bin_path,
                  save_bins_dir,
                  test_params,
                  original_cost,
                  uroboros_dir,
                  # uroboros_env,
                  src_bin_path,
                  env_path):
    # use test_id as the class name
    res =  "class %s(CallableEnv):\n" % test_id
    res += "    def __init__(self):\n"
    res += "        super(%s, self).__init__()\n" % test_id
    res += "        info = CoreutilsInfo(test_id=\'%s\', exe_bin_path=\'%s\', save_bins_dir=\'%s\', test_params=%s, uroboros_dir=\'%s\', uroboros_env=uroboros_env, src_bin_path=\'%s\')\n" % (
    test_id, exe_bin_path, save_bins_dir, str(test_params), uroboros_dir, src_bin_path)
    res += "        self._env = CoreutilsEnv(info, \'%s\', max_itr=iteration_num, test_times=test_times, _original_cost=%s)\n\n" % (env_path, str(original_cost))
    return res


def create_an_gym_env(test_id,
                      exe_bin_path,
                      save_bins_dir,
                      test_params,
                      original_cost,
                      uroboros_dir,
                      src_bin_path,
                      env_path):
    res = "%s_info = CoreutilsInfo(test_id=\'%s\', exe_bin_path=\'%s\', save_bins_dir=\'%s\', test_params=%s, uroboros_dir=\'%s\', uroboros_env=uroboros_env, src_bin_path=\'%s\')\n" % (
    test_id, test_id, exe_bin_path, save_bins_dir, str(test_params), uroboros_dir, src_bin_path)
    res += "%s = CoreutilsEnv(%s_info, \'%s\', max_itr=iteration_num, test_times=test_times, _original_cost=%s)\n\n" % (test_id, test_id, env_path, str(original_cost))
    return res


def build_gym_env2(bin_name, params, cost_time, mode='train'):
    result = ''
    global src_uroboros
    pe_str = '%s_envs = [' % mode
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    base_dir = os.path.join(output_dir, mode)
    os.mkdir(base_dir)
    base_exe_bin_path = os.path.join(base_dir, 'test')
    os.mkdir(base_exe_bin_path)
    base_save_bins_dir = os.path.join(base_dir, 'save')
    os.mkdir(base_save_bins_dir)
    base_env_path = os.path.join(base_dir, 'env')
    os.mkdir(base_env_path)
    base_uroboros_dir = os.path.join(base_dir, 'uroboros')
    os.mkdir(base_uroboros_dir)
    for i in range(1, 7):
        count = i
        test_id = bin_name + '_' + mode + '_env' + '_' + str(count)
        exe_bin_path = os.path.join(base_exe_bin_path, '%s_%d' % (mode, count))
        save_bins_dir = os.path.join(base_save_bins_dir, '%s_%d' % (mode, count))
        os.mkdir(save_bins_dir)
        env_path = os.path.join(base_env_path, '%s_%d' % (mode, count))
        os.mkdir(env_path)
        uroboros_dir = os.path.join(base_uroboros_dir, '%s_%d' % (mode, count))
        src_bin_path = os.path.join(src_coreutils_path, bin_name)
        if src_uroboros is None:
            ret = os.system('git clone %s %s' % (uroboros_url, uroboros_dir))
            assert ret == 0, 'failed to clone uroboros'
            src_uroboros = uroboros_dir
        else:
            os.system('cp -r %s %s' % (src_uroboros, uroboros_dir))
        env_str = create_an_gym_env(test_id, exe_bin_path, save_bins_dir, params, cost_time, uroboros_dir, src_bin_path, env_path)
        result += env_str + '\n'
        pe_str += test_id + ', '
    pe_str = pe_str[:-2] + ']'
    return result, pe_str

if __name__ == "__main__":
    callable_file = sys.argv[2] + '.py'
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    if sys.argv[1] == 'tf_agents':
        raise NotImplementedError()
    elif sys.argv[1] == 'gym':
        raise NotImplementedError()
    elif sys.argv[1] == 'gym2':
        local_head_lines = gym_head_lines
        bin_name = sys.argv[3]
        params, time_cost = train_bin_dict[bin_name]
        train_define_str, train_pe_str = build_gym_env2(bin_name, params, time_cost)
        eval_define_str, eval_pe_str = '', ''  #build_gym_env(eval_bin_dict, 'eval')
    else:
        assert False

    with open(callable_file, 'w') as f:
        f.write(local_head_lines)
        f.write('\n#trainning environments\n')
        f.write(train_define_str)
        f.write('\n#evaluating environments\n')
        f.write(eval_define_str)
        f.write(train_pe_str)
        f.write('\n')
        f.write(eval_pe_str)
        f.write('\n')



