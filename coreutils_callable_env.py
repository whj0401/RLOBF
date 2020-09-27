from src.coreutils_gym_env import *

iteration_num = 20
test_times=5
#trainning environments
md5sum_train_env_1_info = CoreutilsInfo(test_id='md5sum_train_env_1', exe_bin_path='./output/train/test/train_1', save_bins_dir='./output/train/save/train_1', test_params=['./dir4test/a'], uroboros_dir='./output/train/uroboros/train_1', uroboros_env=uroboros_env, src_bin_path='./samples/md5sum')
md5sum_train_env_1 = CoreutilsEnv(md5sum_train_env_1_info, './output/train/env/train_1', max_itr=iteration_num, test_times=test_times, _original_cost=None)


md5sum_train_env_2_info = CoreutilsInfo(test_id='md5sum_train_env_2', exe_bin_path='./output/train/test/train_2', save_bins_dir='./output/train/save/train_2', test_params=['./dir4test/a'], uroboros_dir='./output/train/uroboros/train_2', uroboros_env=uroboros_env, src_bin_path='./samples/md5sum')
md5sum_train_env_2 = CoreutilsEnv(md5sum_train_env_2_info, './output/train/env/train_2', max_itr=iteration_num, test_times=test_times, _original_cost=None)


md5sum_train_env_3_info = CoreutilsInfo(test_id='md5sum_train_env_3', exe_bin_path='./output/train/test/train_3', save_bins_dir='./output/train/save/train_3', test_params=['./dir4test/a'], uroboros_dir='./output/train/uroboros/train_3', uroboros_env=uroboros_env, src_bin_path='./samples/md5sum')
md5sum_train_env_3 = CoreutilsEnv(md5sum_train_env_3_info, './output/train/env/train_3', max_itr=iteration_num, test_times=test_times, _original_cost=None)


md5sum_train_env_4_info = CoreutilsInfo(test_id='md5sum_train_env_4', exe_bin_path='./output/train/test/train_4', save_bins_dir='./output/train/save/train_4', test_params=['./dir4test/a'], uroboros_dir='./output/train/uroboros/train_4', uroboros_env=uroboros_env, src_bin_path='./samples/md5sum')
md5sum_train_env_4 = CoreutilsEnv(md5sum_train_env_4_info, './output/train/env/train_4', max_itr=iteration_num, test_times=test_times, _original_cost=None)


md5sum_train_env_5_info = CoreutilsInfo(test_id='md5sum_train_env_5', exe_bin_path='./output/train/test/train_5', save_bins_dir='./output/train/save/train_5', test_params=['./dir4test/a'], uroboros_dir='./output/train/uroboros/train_5', uroboros_env=uroboros_env, src_bin_path='./samples/md5sum')
md5sum_train_env_5 = CoreutilsEnv(md5sum_train_env_5_info, './output/train/env/train_5', max_itr=iteration_num, test_times=test_times, _original_cost=None)


md5sum_train_env_6_info = CoreutilsInfo(test_id='md5sum_train_env_6', exe_bin_path='./output/train/test/train_6', save_bins_dir='./output/train/save/train_6', test_params=['./dir4test/a'], uroboros_dir='./output/train/uroboros/train_6', uroboros_env=uroboros_env, src_bin_path='./samples/md5sum')
md5sum_train_env_6 = CoreutilsEnv(md5sum_train_env_6_info, './output/train/env/train_6', max_itr=iteration_num, test_times=test_times, _original_cost=None)



#evaluating environments
train_envs = [md5sum_train_env_1, md5sum_train_env_2, md5sum_train_env_3, md5sum_train_env_4, md5sum_train_env_5, md5sum_train_env_6]

