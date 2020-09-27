# -*- coding: utf-8 -*-

from tf_agents.environments.py_environment import PyEnvironment

class CallableEnv(PyEnvironment):

    def __init__(self):
        super(CallableEnv, self).__init__()
        self._env = None

    def _step(self, action):
        return self._env._step(action)

    def action_spec(self):
        return self._env.action_spec()

    def observation_spec(self):
        return self._env.observation_spec()

    def _reset(self):
        return self._env._reset()


