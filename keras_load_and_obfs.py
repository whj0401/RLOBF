# -*- coding: utf-8 -*-
import os
import sys
import gym
import numpy as np
import random
import keras
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, Bidirectional
from keras.optimizers import Adam

from collections import deque

from src.coreutils_gym_env import CoreutilsEnv, CoreutilsInfo
from src.utils.config import uroboros_env, instrs_size, max_ops_len
from coreutils_callable_env import *
import src.utils.log as log

from multiprocessing import Process, Pipe
from time import sleep


def sub_process_env_step(env, conn):
    done = False
    while not done:
        action = conn.recv()
        res = env.step(action)
        done = res[2]
        conn.send(res)
    conn.close()


class DQN:
    def __init__(self, env, model_path=None):
        self.env     = env
        self.memory  = deque(maxlen=1000)

        self.gamma = 1.0
        self.epsilon = 0.01
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99
        self.learning_rate = 0.0001
        self.learning_decay = 0.5
        self.tau = .125

        self._action_space = self.env.action_space

        if model_path:
            self.load_model(model_path)
        else:
            self.init_model()


    def init_model(self):
        self.model = self.create_model()
        self.target_model = self.create_model()

    def load_model(self, model_path):
        try:
            self.target_model = self.create_model()
            self.target_model.build(input_shape=(None, 1, max_ops_len))
            self.target_model.load_weights(model_path)
            self.model = self.target_model
        except Exception as e:
            log.log('cannot load model from %s' % model_path, log.LogType.ERROR)
            log.log(str(e), log.LogType.ERROR)
            self.init_model()

    def create_model(self):
        model   = Sequential()
        state_shape  = self.env.observation_space.shape
        #model.add(Embedding(input_dim=instrs_size, output_dim=2, input_length=state_shape[0]))
        model.add(Bidirectional(LSTM(units=512, return_sequences=True)))
        model.add(LSTM(units=512))
        model.add(Dense(units=512, activation='relu'))
        model.add(Dense(units=self._action_space.n))
        model.compile(loss="mean_squared_error",
            optimizer=Adam(lr=self.learning_rate))
        return model

    def set_lr(self, lr):
        current_lr = keras.backend.eval(self.model.optimizer.lr)
        log.log('set learning rate from %f to %f' % (current_lr, lr), log.LogType.WARNING)
        self.learning_rate = lr
        keras.backend.set_value(self.model.optimizer.lr, self.learning_rate)
        keras.backend.set_value(self.target_model.optimizer.lr, self.learning_rate)

    def reduce_lr(self):
        new_learning_rate = self.learning_rate * self.learning_decay
        log.log('reduce learning rate from %f to %f' % (self.learning_rate, new_learning_rate))
        self.learning_rate = new_learning_rate
        keras.backend.set_value(self.model.optimizer.lr, self.learning_rate)
        keras.backend.set_value(self.target_model.optimizer.lr, self.learning_rate)

    def act(self, state):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return self._action_space.sample()
        return np.argmax(self.model.predict(state)[0])

    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])

    def replay(self):
        batch_size = 128
        if len(self.memory) < batch_size:
            batch_size = len(self.memory)

        samples = random.sample(self.memory, batch_size)
        X = []
        y = []
        for sample in samples:
            state, action, reward, new_state, done = sample
            target = self.target_model.predict(state)
            if done:
                target[0][action] = reward
            else:
                Q_future = max(self.target_model.predict(new_state)[0])
                target[0][action] = reward + Q_future * self.gamma
            X.append(state)
            y.append(target)
        X = np.array(X).reshape(batch_size, 1, max_ops_len)
        y = np.array(y).reshape(batch_size, self._action_space.n)
        log.log('training ...', log.LogType.INFO)
        self.model.fit(X, y, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn, iteration):
        if not os.path.isdir(fn):
            os.mkdir(fn)
        file_path = os.path.join(fn, 'dqn_model-%d' % iteration)
        self.model.save(file_path)


def finish_an_episode(envs, dqn_agent):
    num = len(envs)
    finished = [False for _ in range(num)]
    cur_states = [env.reset().reshape(1, 1, max_ops_len) for env in envs]
    conns = [Pipe() for _ in range(num)]
    processes = [Process(target=sub_process_env_step, args=(envs[idx], conns[idx][1])) for idx in range(num)]
    for p in processes:
        p.start()
    while True:
        has_active = False
        actions = [-1 for _ in range(num)]
        for idx in range(num):
            if not finished[idx]:
                has_active = True
                action = dqn_agent.act(cur_states[idx])
                conns[idx][0].send(action)
                sleep(0.5)
                actions[idx] = action
        if not has_active:
            break
        for idx in range(num):
            if not finished[idx]:
                new_state, reward, done, log_dict = conns[idx][0].recv()
                new_state = new_state.reshape(1, 1, max_ops_len)
                if log_dict['reset']:  # error process
                    finished[idx] = True
                    continue
                else:
                    finished[idx] = done
                    if done:
                        conns[idx][0].close()
                dqn_agent.remember(cur_states[idx], actions[idx], reward, new_state, done)
                cur_states[idx] = new_state
    for p in processes:
        p.join()



def main(model_path):
    num_iterations  = 10

    dqn_agent = DQN(env=train_envs[0], model_path=model_path)
    for iteration in range(1, num_iterations+1):
        for env in train_envs:
            env.set_episode_count(iteration)
        finish_an_episode(train_envs, dqn_agent)

if __name__ == "__main__":
    main(sys.argv[1])
