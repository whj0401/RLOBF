import gym
from gym.utils import seeding
from gym import utils
from gym import error, spaces
from time import sleep

import numpy as np

from src.utils.bin2analysable import *
from src.utils.cmp_bins import *
from src.utils.running_time import *
from src.utils.log import *

similarity_threshold = 0.68  # the accurate value is 0.6853390874585447
#similarity_threshold = 0.6
c1 = -0.05
#c1 = 0.05  # a positive score for each step, which encourges the system to do obfuscation
c2 = 0.37486390900521455
#c2 = 0.0 # here we simply ignore the overhead
c3 = 0.329109429463589 # alpha
c4 = (-c1) * 100
c5 = c2 * 10  # the similarity is lower than the threshold, we do not count on it
c6 = c3 * 1

_dtype = np.int16


class IDAException(Exception):
    def __init__(self, ret):
        super(IDAException, self).__init__('ida pro returned: %d' % ret)


class BinDiffException(Exception):
    def __init__(self, ret):
        super(BinDiffException, self).__init__('bindiff returned: %d' % ret)


class CoreutilsInfo:

    def __init__(self, test_id, exe_bin_path, save_bins_dir, test_params, uroboros_dir, uroboros_env,
                 src_bin_path=None):
        self.id = test_id
        self.exe_bin_path = os.path.abspath(exe_bin_path)  # the test will run binary here
        self.save_dir = os.path.abspath(save_bins_dir)
        log('clear directory: %s' % self.save_dir, LogType.INFO)
        if os.path.isdir(self.save_dir):
            os.system('sudo rm -r {}'.format(self.save_dir))
        os.mkdir(self.save_dir)

        if src_bin_path is None:
            self.src_bin_path = os.path.abspath(self.exe_bin_path)
        else:
            self.src_bin_path = os.path.abspath(src_bin_path)

        self.uroboros_dir = os.path.abspath(uroboros_dir)
        self.uroboros_env = os.path.abspath(uroboros_env)

        self.itr_count = 0
        self.current_bin_path = self._get_current_bin_path()
        self._next_bin_path = None

        self.reset()

        log('cp ' + self.src_bin_path + ' ' + self.exe_bin_path, LogType.RUN_CMD)
        os.system('cp ' + self.src_bin_path + ' ' + self.exe_bin_path)

        self.test_cmd = self.exe_bin_path + ' ' + ' '.join(test_params)
        log('future test cmd: ' + self.test_cmd, LogType.INFO)
        self.test_cmd_args = [self.exe_bin_path] + test_params

    def reset(self):
        self.itr_count = 0
        self.current_bin_path = self._get_current_bin_path()
        self._next_bin_path = None
        if os.path.isdir(self.save_dir):
            os.system('sudo rm -r ' + self.save_dir)
        os.mkdir(self.save_dir)

    def mv_save(self, des):
        os.system('sudo mv %s %s' % (self.save_dir, des))

    def get_next_output_bin_path(self):
        if self._next_bin_path is None:
            self._next_bin_path = os.path.join(self.save_dir, self.id + '_' + str(self.itr_count + 1))
        return self._next_bin_path

    def _get_current_bin_path(self):
        if self.itr_count == 0:
            return self.src_bin_path
        return os.path.join(self.save_dir, self.id + '_' + str(self.itr_count))

    def mv2_next_iteration(self):
        self.current_bin_path = self.get_next_output_bin_path()
        self._next_bin_path = None
        self.itr_count += 1

    def get_div_cmd(self, action):
        div_cmd = '{}/bin/python uroboros.py {} -i 1 -d {} -o {}'.format(self.uroboros_env,
                                                                         self.current_bin_path,
                                                                         action, self.get_next_output_bin_path())
        cwd = self.uroboros_dir + '/src'
        return div_cmd, cwd

    def get_cmd_cp_output2test_dir(self):
        return 'cp {} {}'.format(self.get_next_output_bin_path(), self.exe_bin_path)


class CoreutilsEnv(gym.core.Env):

    def __init__(self, test_info: CoreutilsInfo, out_dir, max_itr=100, test_times=5, _original_cost=None):
        log('initializing environment: ' + test_info.id, LogType.INFO)
        assert test_times > 2
        super(CoreutilsEnv, self).__init__()
        # only 0-8 modes, inline_func is not predictable, and basic block merge has some problems
        self._action_set = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}  # remove 3, it is too powerful
        self.action_space = spaces.Discrete(len(self._action_set))
        self.observation_space = spaces.Space(shape=(max_ops_len,), dtype=_dtype)
        self._episode_ended = False
        self.max_iteration = max_itr
        self.test_times = test_times
        self._episode_count = 0

        self.test_info = test_info
        self.out_dir = out_dir
        if os.path.isdir(self.out_dir):
            os.system('sudo rm -r {}'.format(self.out_dir))
        os.mkdir(self.out_dir)

        # set files to store running info
        self._stat_files = [os.path.join(self.out_dir, self.test_info.id + '.perf-stat-' + str(idx)) for idx in range(self.test_times)]

        self._src_bin_export = self._get_bin_export_path(self.test_info.current_bin_path)
        # speed up the test process, the exported file exists
        if not os.path.isfile(self._src_bin_export):
            ret = ida_bin_export_info(self.test_info.current_bin_path, self._src_bin_export)
            if ret != 0:
                raise IDAException(ret)
            # assert ret == 0, "bindiff return errors, return value: %d" % ret

        if _original_cost is None:
            self._original_cycles_cost = self._get_performance(mode=0)
            assert self._original_cycles_cost > 0, "error of perf!"
        else:
            self._original_cycles_cost = _original_cost

        self._cycles_list = [self._original_cycles_cost]  # idx=0 is the original binary's running clock
        self._reward_list = []
        self._action_list = []

        self._original_state = bin2state(self.test_info.current_bin_path)

        self._state = self._original_state
        self._cycles_cost = self._original_cycles_cost
        self._similarity = 1.0

        self._reward_records_file = os.path.join(self.out_dir, 'reward_records_{}.txt'.format(self.test_info.id))
        self._error_log = os.path.join(self.out_dir, 'error_log_{}.txt'.format(self.test_info.id))
        self._error_count = 0

        self._uroboros_meet_error = False
        self._uroboros_error_count = 0
        self._diversify_output_file = os.path.join(self.out_dir, 'div_all_output.txt')

        log('environment \'%s\' initialized' % self.test_info.id, LogType.INFO)

    def step(self, action):
        return self._step(action)

    def reset(self):
        return self._reset()[0]

    def render(self, mode='human'):
        return

    def close(self):
        return

    def seed(self, seed=None):
        return seed

    def set_episode_count(self, count):
        self._episode_count = count

    def save_current_episode(self):
        des_path = os.path.join(self.out_dir, 'save_episode_%d' % self._episode_count)
        self.test_info.mv_save(des_path)

    def _get_bin_export_path(self, bin_path):
        # store the binExport file at the same folder
        return os.path.abspath(bin_path) + '.binExport'

    def _get_bins_similarity(self, bin1, bin2, bin1_exported=True, bin2_exported=False):
        """
        :param bin1: the path of a binary which has an existing .binExport file
        :param bin2: the file needs to be analysed
        :param bin1_exported: if bin1.binExport exists, True; else, False
        :param bin2_exported: if bin2.binExport exists, True; else, False
        :return: similarity of bin1 and bin2
        """
        bin1_export = self._get_bin_export_path(bin1)
        if not bin1_exported:
            ret = ida_bin_export_info(bin1, bin1_export)
            if ret != 0:
                raise IDAException(ret)
            # assert ret == 0, str(ret)
        bin2_export = self._get_bin_export_path(bin2)
        if not bin2_exported:
            ret = ida_bin_export_info(bin2, bin2_export)
            if ret != 0:
                raise IDAException(ret)
            # assert ret == 0, str(ret)
        ret, export = bindiff_similarity(bin1_export, bin2_export, out_dir=self.out_dir)
        if ret != 0:
            raise BinDiffException(ret)
        assert ret == 0, str(ret)
        sim_file = os.path.join(self.out_dir, 'similarity_{}-{}'.format(os.path.basename(bin1), os.path.basename(bin2)))
        sim, _ = read_bindiff_export(bindiff_file_path=export, output_file=sim_file)
        return sim

    def _reset(self):
        self._state = self._original_state
        self._cycles_cost = self._original_cycles_cost
        self._similarity = 1.0
        self._cycles_list = [self._original_cycles_cost]
        self._reward_list.clear()
        self._action_list.clear()
        self.test_info.reset()
        return np.array(self._state, dtype=_dtype), 0.0, True, {'reset': True}

    def _get_diversified_bin(self, action):
        div_cmd, cwd = self.test_info.get_div_cmd(action)
        # div_cmd = '(' + div_cmd + ') &> ' + self._diversify_output_file
        log('cd {} && '.format(cwd) + div_cmd, LogType.RUN_CMD)
        # ret = os.system('cd {} && '.format(cwd) + div_cmd)
        with open(self._diversify_output_file, 'w') as out:
            old_cwd = os.getcwd()
            os.chdir(cwd)
            p = Popen(div_cmd.split(' '), stdout=out, stderr=out)
            ret = p.wait()
            os.chdir(old_cwd)
            if ret != 0:
                self._uroboros_meet_error = True
        return self.test_info.get_next_output_bin_path()

    def _cp_next_file2test_dir(self):
        cp_cmd = self.test_info.get_cmd_cp_output2test_dir()
        log(cp_cmd, LogType.RUN_CMD)
        count = 0
        while os.system(cp_cmd) != 0 and count < 600:
            sleep(1)
            count += 1

    def _analyse_bin(self):
        ob = bin2state(self.test_info.current_bin_path)
        cycles = self._get_performance()
        return ob, cycles

    def _get_performance(self, mode=0):
        # _ = run_cmd_with_perf_stat_subshell(cmd=test_cmd, stat_file_path=stat_file)
        # run multiprocesses to test the running time, then return average
        sub_ps = []
        total_task_clocks = 0.0
        log(str(self.test_times) + ' subprocesses: perf stat ' + self.test_info.test_cmd, LogType.RUN_CMD)
        for stat_file in self._stat_files:
            sub_ps.append(run_cmd_with_perf_stat(cmd=self.test_info.test_cmd_args, stat_file_path=stat_file, repeat=10))
        meets_error = False
        for sub_p in sub_ps:
            try:
                outs, errs = sub_p.communicate(timeout=50.0)
                if errs:
                    log(errs, LogType.ERROR, True)
                    meets_error = True
            except Exception:
                sub_p.kill()
                #sub_p.communicate()
                meets_error = True
        if meets_error:
            # this iteration is useless, kill all children and return -1
            for sub_p in sub_ps:
                if sub_p.poll() is None:
                    sub_p.kill()
                #    sub_p.communicate()
            return -1

        # make sure all children have terminated
        time_count = 0
        while time_count < 51:
            has_alive = False
            for sub_p in sub_ps:
                if sub_p.poll() is None:
                    has_alive = True
                    break
            if has_alive:
                time_count += 1
                sys.sleep(1)
            else:
                break
            if time_count == 52:
                for sub_p in sub_ps:
                    if sub_p.poll() is None:
                        sub_p.kill()
                #        sub_p.communicate()

        min_task_clock = 10000000.0
        for stat_file in self._stat_files:
            task_clock = get_perf_stat_result(stat_file)
            min_task_clock = min(min_task_clock, task_clock)
            total_task_clocks += task_clock
        if mode == 0:
            return total_task_clocks / self.test_times
        elif mode == 1:
            return min_task_clock

    def _is_end(self, similarity):
        return similarity < similarity_threshold or self.test_info.itr_count >= self.max_iteration
        # return self.test_info.itr_count >= self.max_iteration

    def _save_error_status(self, action):
        target_dir_name = self.test_info.uroboros_dir + '/src/error_' + str(
            self._uroboros_error_count) + '_mode_' + str(action)
        while os.path.isdir(target_dir_name):
            self._uroboros_error_count += 1
            target_dir_name = self.test_info.uroboros_dir + '/src/error_' + str(
                self._uroboros_error_count) + '_mode_' + str(action)
        os.system('mv {} {}'.format(self.test_info.uroboros_dir + '/src/workdir_1',
                                    self.test_info.uroboros_dir + '/src/error_' + str(
                                        self._uroboros_error_count) + '_mode_' + str(action)))
        os.system('mv {} {}/'.format(self._diversify_output_file, target_dir_name))

    def _step(self, action):
        #if action >= 3:
        #    action += 1
        next_bin = self._get_diversified_bin(action)
        if self._uroboros_meet_error:
            self._uroboros_meet_error = False
            self._uroboros_error_count += 1
            # save the error status
            self._save_error_status(action)
            return self._reset()
        self._cp_next_file2test_dir()
        # compare current and next
        # 9.1
        # similarity = self._get_bins_similarity(self.test_info.current_bin_path, next_bin, True, False)
        # original_sim = self._get_bins_similarity(self.test_info.src_bin_path, next_bin, True, True)
        try:
            # the BinExport plugin may occur unknown errors, not sure.
            original_sim = self._get_bins_similarity(self.test_info.src_bin_path, next_bin, True, False)
            #similarity = self._get_bins_similarity(self.test_info.current_bin_path, next_bin, True, False)
            #original_sim = self._get_bins_similarity(self.test_info.src_bin_path, next_bin, True, True)
        except (IDAException, BinDiffException) as e:
            print(str(e))
            print('current iteration is not usable')
            self._action_list.append(str(action))
            self._error_count += 1
            os.system('cp %s %s' % (next_bin, self.out_dir))
            with open(self._error_log, 'a') as f:
                f.write('\nrewards   : ' + str(self._reward_list) +
                        '\ncycles    : ' + str(self._cycles_list) +
                        '\nactions   : ' + str(self._action_list) +
                        '\niteration : ' + str(self.test_info.itr_count) + '\n')
            return self._reset()

        self.test_info.mv2_next_iteration()
        ob, cycles = self._analyse_bin()
        if cycles <= 0:
            # software may never end (error in diversification)
            self._save_error_status(action)
            return self._reset()
        # before 1.10
        reward = c1 - c2 * cycles / self._original_cycles_cost + c3 / original_sim
        #reward = c1 - c2 * cycles / self._cycles_cost + c3 / similarity
        self._reward_list.append(reward)
        self._cycles_list.append(cycles)
        self._action_list.append(str(action))
        self._state = ob
        self._cycles_cost = cycles
        self._similarity = original_sim
        if self._is_end(original_sim):
            # set the final step reward, the final score should pay no attention to how many iterations have been taken
            if original_sim <= similarity_threshold:
                reward = c4 - c5 * (cycles / self._original_cycles_cost - 1.0)
            else:
                reward = c1 - c5 * (cycles / self._original_cycles_cost - 1.0)
            self._reward_list[-1] = reward
            with open(self._reward_records_file, 'a') as f:
                f.write('\nrewards   : ' + str(self._reward_list) +
                        '\ncycles    : ' + str(self._cycles_list) +
                        '\nactions   : ' + str(self._action_list) +
                        '\niteration : ' + str(self.test_info.itr_count) +
                        '\nsimilarity: ' + str(original_sim) + '\n')
            self.save_current_episode()
            return np.array(ob, dtype=_dtype), reward, True, {'reward':reward, 'cycles':cycles, 'action':action, 'iteration':self.test_info.itr_count, 'reset':False}
        else:
            return np.array(ob, dtype=_dtype), reward, False, {'reward':reward, 'cycles':cycles, 'action':action, 'iteration':self.test_info.itr_count, 'reset':False}
