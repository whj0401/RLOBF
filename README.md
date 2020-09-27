# Use a RL model to select diversification mode

# Environment Setting
Please install IDA Pro (7.3), bindiff, sqlite3, perf, tensorflow(>=2.0) and keras first.

To install the python2 environment for uroboros, please refer to the `uroboros-diversification/README.md`


Please modify values in `config.json`

`uroboros_env` is the python virtualenv for running uroboros `$uroboros_env/bin/python` must exist

`prj_dir` is the directory for this project

`ida_pro_path` is the executable of ida pro. `idat64` is tested.

`bindiff_path` is the executable of bindiff, the default path of this is `/opt/bindiff/bin/bindiff`

`perf_path` is the executabtle of perf, the default path of this is `/usr/bin/perf`

If modify this json file does not work, you could modify `src/utils/config.py` directly.

Please modify the `py` in `run_keras.sh`.


# Build a Coreutil Case to Train
`./build_coreutils.sh [bin_name]`

Please see provided cases in `./samples`

# Training Model
`sh ./run_with_screen.sh keras`

This will need root right, because we use perf to evaluate the running time of a program.

You need to make sure there is at least 25GB space on current disk to save checkpoints, or you can modify the `checkpoints_dir` parameter in `keras_rl.py`

# Using Models
The models are saved on disk with file names `dqn_model_[iteration]`. Use your keras environment to run

`python3 ./keras_load_and_obfs.py [model_path]`

Please note the above command will clean contents in the output directory. See the created `coreutils_callable_env.py`. The default output directory is `./output`

# Explanation
the data is in `./explanation`, and these data comes from running `./obfs_explainer.py` and `./read_html_explanation.py`

# Test other binaries
To run cases not provided, please look into file `coreutils_env_config.py`

Please modify these directories variables in `coreutils_env_config.py`

`src_coreutils_path` and `output_dir`, the binary being tested must exist in `src_coreutils_path`, and `train_bin_dict` should add an item.

key is the name of this binary, and value is a tuple of

a.the command to be tested;

b.the time cost of this command. You could initial it with None, or write it manually. Use `sudo perf stat -r [repeat-times] -e task-clock [your command]` to get it.

`python coreutils_env_config.py gym2 coreutils_callable_env`, a file `coreutils_callable_env.py` will be created.
You could change the file name, but change the `import` in `keras_rl.py` at the same time.


