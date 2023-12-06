# MIT License
# 
# Copyright (c) 2023 MiscellaneousStuff
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Hosts a zerorpc server which infers the next action to take given an observation."""

from absl import app
from absl import flags

import zerorpc

import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np

from tlol.models.jinx_model import Model

FLAGS = flags.FLAGS
flags.DEFINE_string("model_path", None, "Trained Jinx PyTorch model weights *.pt")
flags.DEFINE_string("host", "0.0.0.0", "ZeroRPC Host Address")
flags.DEFINE_int("port", 4242, "ZeroRPC Port Number")

class JinxModelRPC(object):
    def __init__(self, model_path):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = Model(in_dim=47, out_dim=81).to(self.device)
        self.model.load_state_dict(\
            torch.load(model_path))
        self.model.eval()

    def infer(self, obs):
        obs = np.array([obs])
        obs = torch.Tensor(obs).to(self.device)
        outputs = self.model(obs).detach().cpu().numpy()
        act = np.argmax(outputs)
        act = int(act)
        return act

def main():
    model_path = FLAGS.model_path
    s = zerorpc.Server(JinxModelRPC(model_path))
    host = FLAGS.host
    port = FLAGS.port
    s.bind(f"tcp://{host}:{port}")
    s.run()

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)