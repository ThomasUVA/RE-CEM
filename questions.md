# Questions 07/01
- Existing implementation is in Tensorflow, convert to Pytorch? `Yes`
- Standard deviation report for 10-fold cross validation `Can't do fraud anyway`
- Procurement fraud dataset not fully publicly available, same for brain imaging `Brain imaging is`

`The model(s) and all the other files needs to be generate the
results should be in separated`

# Questions 10/01
- Reproduce comparison for LIME and LRP? `NO`
- fMRI data set is downloaded, but we do not know how to continue. Corresponding files from the ABIDE Github need C-PAC which is only available in Python 2. 
- Instruction on how to estimate Pearson matrix as described for the fMRI, generally what to do for the (pre-)processing for the fMRI data. `On the backburner`
- template report `Yes, we'll get it in the mail`
- elaboration on variable new_vars in aen_CEM.py
- perform experiment on different dataset, such as Fashion-MNIST `Yes`
- difference between variables with and without self.adv_img vs self.adv_img_s `Figured it out`
- what model is being trained, if any? what does the attack function supposed to mean exactly? `The delta`
- mnist.h5 for MNISTModel pretrained required? `Can be used, also easy to retrain`
- are we expected to train both models (autoencoder-decoder and MNISTModel) from the start up? if so: optimizer specifications for the MNISTModel are not mentioned in the paper `Possible when changing datasets, not necessary for MNIST`

# Questions 14/01
- Should we als report differences in implementation and paper (e.g. 60.000 training examples vs. 55.000 training examples), or only if the results are then different (or not at all)? `Use what they used, unless it really makes a difference (maybe report both then)`
- Setting the random seed? `Report anything on multiple random runs`
- Using ground truth or prediction to compare changing classes (Section 4.4) `Switch w.r.t. classifier, easy to check metric`
- What is this 10000 doing in the max_nontarget_lab_score? `I don't know, makes no sense check -1, target_lab, scaling`
- Loss after training step? `Could be just wrong for the first grad`
- Structure report? `Explain the algorithm and implementation (+changes), setup, most interseting is discussion + broad interpretation noreal broad implementation this is nice and works okayish bt not usable because continous image f.e. target other scientists write optimization formulas`
- Kappa maximum (eq 4/2) `thing in the appendix is just wrong, in the end it doesnt matter, report if it converges to kappa or zero`