#!/bin/bash
py="path/to/python3/with/keras"
`cp keras_rl.py ./output/`
`cp src/coreutils_gym_env.py ./output/`
`cp coreutils_callable_env.py ./output/`
`sudo $py keras_rl.py`

