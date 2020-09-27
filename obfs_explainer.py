# -*- coding: utf-8 -*-
import os
import sys

import numpy as np
import tensorflow as tf
from eli5.lime import TextExplainer
from eli5.lime.samplers import MaskingTextSampler
from keras.layers import Dense, LSTM, Bidirectional
from keras.layers.core import Activation
from keras.models import Sequential
from keras.optimizers import Adam
from sklearn.base import TransformerMixin

from src.utils.bin2analysable import tokenizer
from src.utils.config import max_ops_len


def create_model(act_space=10, lr=0.0001):
    model = Sequential()
    # model.add(Embedding(input_dim=instrs_size, output_dim=2, input_length=state_shape[0]))
    model.add(Bidirectional(LSTM(units=512, return_sequences=True)))
    model.add(LSTM(units=512))
    model.add(Dense(units=512, activation='relu'))
    model.add(Dense(units=act_space))
    model.compile(loss="mean_squared_error",
                  optimizer=Adam(lr=lr))
    return model


def load_model(path):
    model = create_model(act_space=10)
    model.build(input_shape=(None, 1, max_ops_len))
    model.load_weights(path)
    return model


class StrategySelector(TransformerMixin):

    def __init__(self, model):
        super(StrategySelector, self).__init__()
        self.model = model
        self.softmax_model = Sequential([Activation('softmax')])

    @staticmethod
    def preprocess(op_codes):
        res = tokenizer.texts_to_sequences(op_codes)
        for i in range(len(res)):
            if len(res[i]) < max_ops_len:
                res[i].extend([0 for _ in range(max_ops_len - len(res[i]))])
            else:
                res[i] = res[i][:max_ops_len]
        return np.array(res).reshape(len(res), 1, max_ops_len)


    def fit(self, X, y):
        self.model.fit(X, y)

    def predict_proba(self, op_codes):
        X = self.preprocess(op_codes)
        preds = self.model.predict(X)
        softmax = self.softmax_model.predict(preds)
        return softmax

    def predict(self, op_codes):
        print(len(op_codes), file=sys.stderr)
        X = self.preprocess(op_codes)
        return np.argmax(self.model.predict(X))

    def score(self, X, y):
        y_pred = self.prefict(X)
        count = 0
        for i in range(len(y)):
            if y_pred[i] == y[i]:
                count += 1
        return count / len(y)


# opcode_explainer = TextExplainer(random_state=59)

# op_vec = CountVectorizer(ngram_range=(1, 1))
# op_vec = CountVectorizer(token_pattern='[a-z][a-z]*')
ops_sampler = MaskingTextSampler(token_pattern='[a-z][a-z]*', replacement='mov', bow=False, min_replace=0.0,
                                 max_replace=0.5)

iteration = 100
bin_name = 'sum'
with tf.device('/gpu:0'):
    obfs_model = load_model('/home/hwangdz/export-d1/rl-select-div-out-keras-9.7-1-%s/checkpoints/dqn_model-%d'
                            % (bin_name, iteration))
    ss = StrategySelector(obfs_model)
    # opcodes_dir = '/home/hwangdz/coreutils/coreutils-8.28/install_m32/bin/md5funcs_ops'
    opcodes_dir = '/home/hwangdz/git/rl-select-div/only-similarity/explanation/%s_ops_info' % bin_name
    output_dir = 'explanation/%s_html' % bin_name
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    for file_name in os.listdir(opcodes_dir):
        # if file_name != 'dump.s':
        #    continue
        if file_name == 'op_distribution':
            continue
        file_path = os.path.join(opcodes_dir, file_name)
        with open(file_path, 'r') as f:
            op_codes = f.read()
            if len(op_codes) < 20:
                continue
            num_ops = len(op_codes.split())
            op_codes = op_codes.replace('\n', ' ')
            opcode_explainer = TextExplainer(random_state=59, sampler=ops_sampler, n_samples=5000)
            #repeat_times = (len(op_codes.split()) / 100) ** 2
            repeat_times = 1
            for _ in range(repeat_times):
                opcode_explainer.fit(op_codes, ss.predict_proba)
            explanation = opcode_explainer.explain_prediction()._repr_html_()
            with open('explanation/%s_html/explanation-%s.html' % (bin_name, file_name), 'w') as ef:
                ef.write(explanation)
                ef.write('num of opcodes: %d\n' % num_ops)
                ef.write('</br>\n')
                ef.write(op_codes)


