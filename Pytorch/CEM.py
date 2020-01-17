## CEM.py -- Constrastive Explanation Method class in which adversarial
##           attacks are performed to analyze the target pertinent instance.
##
## (C) 2020 UvA FACT AI group

import sys
import torch
import numpy as np
#import torchvision
import fista
import evaluation
from polynomial_decay import poly_lr_scheduler
from torchvision import utils
from torch.autograd import Variable


class CEM:
    def __init__(self, model, mode, AE, batch_size, learning_rate_init,
                 c_init, c_steps, max_iterations, kappa, beta, gamma):
        """
        Constrastive Explanation Method (CEM) class initialization.
        Moreover, CEM is used to perform adversarial attacks with the autoencoder.
        Input:
            - model              : Pytorch CNN prediction model
            - mode               : perform either PN or PP analysis
            - AE                 : autoencoder model for the adversarial attacks
            - batch_size         : number of data instances to be analyzed
            - learning_rate_init : starting learning rate for the optimizer
            - c_init             : starting weight constant of the loss function
            - c_steps            : number of iterations in which the constant c
                                   is adjusted
            - max_iterations     : maximum number of iterations for the analysis
            - kappa              : confidence parameter to measure the distance
                                   between target class and other classes
            - beta               : regularization weight for the L1 loss term
            - gamma              : regularization weight for autoencoder loss
                                   function
        """

        # Initialize the shape for the variables used for pertinent analysis.
        shape = (batch_size, \
                 model.image_size, model.image_size,  model.num_channels)

        # Define model variables
        self.model = model
        self.mode = mode
        self.AE = AE
        self.batch_size = batch_size
        self.lr_init = learning_rate_init
        self.c_init = c_init
        self.c_steps = c_steps
        self.max_iterations = max_iterations
        self.kappa = kappa
        self.beta = beta
        self.gamma = gamma

        # Initialize optimizer.
        #self.adv_img = torch.zeros((shape), dtype=torch.float32, requires_grad=True)
        #self.adv_img_slack = torch.zeros((shape), dtype=torch.float32, requires_grad=True)


    def attack(self, imgs, labs):
        dvc = imgs.device

        def compare(x, y):
            if not isinstance(x, (float, int, np.int64)):
                x = x.clone()
                # x[y] -= self.kappa if self.PP else -self.kappa
                if self.mode == "PP":
                    x[y] -= self.kappa
                elif self.mode == "PN":
                    x[y] += self.kappa
                x = torch.argmax(x)
            if self.mode == "PP":
                return x==y
            elif self.mode == "PN":
                return x!=y

        batch_size = self.batch_size

        # set the lower and upper bounds accordingly
        lower_bound = torch.zeros(batch_size).to(dvc)
        c_start = torch.ones(batch_size).to(dvc) * self.c_init
        upper_bound = torch.ones(batch_size).to(dvc) * 1e10
        # the best l2, score, and image attack
        overall_best_dist = [1e10] * batch_size
        overall_best_attack = [np.zeros(imgs[0].shape)] * batch_size

        for c_steps_idx in range(self.c_steps):
            # completely reset adam's internal state.
            img_batch = imgs[:batch_size]
            label_batch = labs[:batch_size]

            current_step_best_dist = [1e10] * batch_size
            current_step_best_score = [-1] * batch_size

            # set the variables so that we don't have to send them over again
            orig_img = img_batch
            target_lab = label_batch
            self.adv_img = img_batch
            self.adv_img_slack = Variable(img_batch, requires_grad=True)
            self.optimizer = torch.optim.SGD(params=[self.adv_img_slack], lr = self.lr_init)
            utils.save_image(orig_img.squeeze(), 'original_image.png')

            for iteration in range(self.max_iterations):
                # perform the attack
                #self.adv_img, self.adv_img_slack = fista.fista(self.mode, self.beta, iteration, self.adv_img, self.adv_img_slack, orig_img)
                self.optimizer.zero_grad()
                self.optimizer = poly_lr_scheduler(self.optimizer, self.lr_init, iteration)
                loss_no_opt, loss_EN, pred = evaluation.loss(self.model, self.mode, orig_img, self.adv_img, target_lab, self.AE, c_start, self.kappa, self.gamma, self.beta, to_optimize=False)
                loss, _, _ = evaluation.loss(self.model, self.mode, orig_img, self.adv_img_slack, target_lab, self.AE, c_start, self.kappa, self.gamma, self.beta)
                loss.backward(retain_graph=True)
                self.optimizer.step()

                self.adv_img, self.adv_img_slack = fista.fista(self.mode, self.beta, iteration, self.adv_img, self.adv_img_slack, orig_img)

                '''

                z = self.adv_img_slack - orig_img
                adv_img_update = (z > self.beta) * torch.min((self.adv_img_slack - self.beta), torch.tensor(0.5)) + \
                               (torch.abs(z) <= self.beta) * orig_img + \
                               (z < -self.beta) * torch.max((self.adv_img_slack + self.beta), torch.tensor(-0.5))

                z_delta = adv_img_update - orig_img

                if self.mode == "PP":
                    adv_img_update = (z_delta <= 0) * adv_img_update + (z_delta > 0) * orig_img
                elif self.mode == "PN":
                    adv_img_update = (z_delta > 0) * adv_img_update + (z_delta <= 0) * orig_img

                # Slack update.
                zt = iteration / (iteration + torch.tensor(3))
                adv_img_slack_update = adv_img_update + zt * (adv_img_update - self.adv_img)
                z_slack = adv_img_slack_update - orig_img

                if self.mode == "PP":
                    adv_img_slack_update = (z_slack <= 0) * adv_img_slack_update + (z_slack > 0) * orig_img
                elif self.mode == "PN":
                    adv_img_slack_update = (z_slack > 0) * adv_img_slack_update + (z_slack <= 0) * orig_img

                self.adv_img = adv_img_update
                self.adv_img_slack = adv_img_slack_update

                '''

                if iteration%(self.max_iterations//10) == 0:
                    print("iter:{} const:{}". format(iteration, c_start))
                    print("Loss_Overall:{:.4f}". format(loss_no_opt))
                    utils.save_image(self.adv_img.detach().squeeze(), str(c_steps_idx) + '-' + str(iteration) + '-img.png')
                    #print("Loss_L2Dist:{:.4f}, Loss_L1Dist:{:.4f}, AE_loss:{}". format(Loss_L2Dist, Loss_L1Dist, Loss_AE_Dist))
                    #print("target_lab_score:{:.4f}, max_nontarget_lab_score:{:.4f}". format(target_lab_score[0], max_nontarget_lab_score_s[0]))
                    #print("")
                    sys.stdout.flush()

                for batch_idx,(dist, score, the_adv_img) in enumerate(zip(loss_EN, pred, self.adv_img)):
                    if dist < current_step_best_dist[batch_idx] and compare(score, torch.argmax(label_batch[batch_idx], -1)):
                        current_step_best_dist[batch_idx] = dist
                        current_step_best_score[batch_idx] = torch.argmax(score, -1)
                    if dist < overall_best_dist[batch_idx] and compare(score, torch.argmax(label_batch[batch_idx], -1)):
                        overall_best_dist[batch_idx] = dist
                        overall_best_attack[batch_idx] = the_adv_img

            # adjust the constant as needed
            for batch_idx in range(batch_size):
                if compare(current_step_best_score[batch_idx], torch.argmax(label_batch[batch_idx], -1)) and current_step_best_score[batch_idx] != -1:
                    # success, divide const by two
                    upper_bound[batch_idx] = min(upper_bound[batch_idx], c_start[batch_idx])
                    if upper_bound[batch_idx] < 1e9:
                        c_start[batch_idx] = (lower_bound[batch_idx] + upper_bound[batch_idx])/2
                else:
                    # failure, either multiply by 10 if no solution found yet
                    #          or do binary search with the known upper bound
                    lower_bound[batch_idx] = max(lower_bound[batch_idx], c_start[batch_idx])
                    if upper_bound[batch_idx] < 1e9:
                        c_start[batch_idx] = (lower_bound[batch_idx] + upper_bound[batch_idx])/2
                    else:
                        c_start[batch_idx] *= 10

        # return the best solution found
        return overall_best_attack[0].unsqueeze(0)
        # return overall_best_attack.reshape((1,) + overall_best_attack.shape)
