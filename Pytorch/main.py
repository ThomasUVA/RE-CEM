## main.py -- sample code to test attack procedure
##
## Copyright (C) 2018, IBM Corp
##                     Chun-Chen Tu <timtu@umich.edu>
##                     PaiShun Ting <paishun@umich.edu>
##                     Pin-Yu Chen <Pin-Yu.Chen@ibm.com>
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

## (C) 2020 Changes by UvA FACT AI group [Pytorch conversion]

import os
import sys
import numpy as np
import random
import time
from setup_mnist import MNIST, MNISTModel
import torch
from torch import cuda
import utils as util
from CEM import CEM

def main(image_id, arg_max_iter=10, c_steps=9, init_const=10.0, mode="PN",
         kappa=100, beta=1e-1, gamma=0, dir='results', seed=121):
    dvc = 'cuda:0' if cuda.is_available() else 'cpu'
    # random.seed(seed)
    # np.random.seed(seed)

    #Load autoencoder and MNIST dataset.
    # AE_model = util.load_AE("mnist_AE_weights").to(dvc)
    AE_model = util.AE(torch.load('models/MNIST_AE.pt')).to(dvc)
    data, model =  MNIST(dvc), MNISTModel(torch.load('models/MNIST_MNISTModel.pt')).to(dvc)

    # Get model prediction for image_id.
    image = data.test_data[image_id].unsqueeze(0)
    orig_prob, orig_class, orig_prob_str = util.model_prediction(model, image)
    target_label = orig_class

    orig_img, target = util.generate_data(data, image_id, target_label)
    print("Image:{}, infer label:{}".format(image_id, target_label))

    # Create adversarial image from original image.
    attack = CEM(model, mode, AE_model, batch_size=1, learning_rate_init=1e-2,
                 c_init=init_const, c_steps=c_steps, max_iterations=arg_max_iter,
                 kappa=kappa, beta=beta, gamma=gamma)
    adv_img = attack.attack(orig_img, target)

    # Calculate probability classes for adversarial and delta image.
    adv_prob, adv_class, adv_prob_str = util.model_prediction(model, adv_img)
    delta_prob, delta_class, delta_prob_str = util.model_prediction(model, orig_img-adv_img)

    # Print some info.
    INFO = f"\n\
  [INFO]\n\
  id:          {image_id},      \n\
  kappa:       {kappa},         \n\
  Orig class:  {orig_class},    \n\
  Adv class:   {adv_class},     \n\
  Delta class: {delta_class},   \n\
  Orig prob:   {orig_prob_str}, \n\
  Adv prob:    {adv_prob_str},  \n\
  Delta prob:  {delta_prob_str} \n"
    print(INFO)

    #Save image to Results
    suffix = f"id{image_id}_Orig{orig_class}_Adv{adv_class}_Delta{delta_class}"
    save_dir = f"{dir}/{mode}_ID{image_id}_Gamma_{gamma}_Kappa_{kappa}"
    os.system(f"mkdir -p {save_dir}")
    util.save_img(orig_img, f"{save_dir}/Orig_original{orig_class}")
    util.save_img(adv_img, f"{save_dir}/Adv_{suffix}")
    util.save_img(torch.abs(orig_img-adv_img)-0.5, f"{save_dir}/Delta_{suffix}")

    sys.stdout.flush()

main(image_id=2950, mode="PP")
