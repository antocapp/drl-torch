
Fast, modular reference implementation of Deep Reinforcement Learning algorithms in PyTorch.


Memory:

Replay Buffer
Prioritised Replay Buffer
-TD loss to regulate priority




######### NETWORKS #############
-init
-forward
-action 

DQN
-High-dim state (CNN), low dim state (FC)
Double DQN
NoisyNet (exploration in net weights with prioritised buffer) - https://arxiv.org/abs/1706.10295
Distributional DQN C51 - https://arxiv.org/pdf/1707.06887.pdf
Rainbow DQN - https://arxiv.org/pdf/1710.02298.pdf
Distributional DQN with Quantile Regression - https://arxiv.org/pdf/1710.10044.pdf
Hierarchical DQN - https://arxiv.org/pdf/1604.06057.pdf

A2C, A3C - https://blog.openai.com/baselines-acktr-a2c/#a2canda3c
GAE - https://arxiv.org/pdf/1506.02438.pdf
PPO - https://arxiv.org/pdf/1707.06347.pdf
Actor-Critic with Experience Replay - https://arxiv.org/pdf/1611.01224.pdf
DDPG - https://arxiv.org/abs/1509.02971
Twin Dueling DDPG - https://arxiv.org/pdf/1802.09477.pdf


Explorations:
-**kwargs
Epsilon, Ornstein Uhlenbeck


Losses:
- batch, model/models, replay buffer or environment, optimiser, 
- backward, optimisation step 
- return loss 

Temporal Difference Loss
PPO Loss

Production:

TRAIN
(train, validation, test with debug)
- # episodes, environment, batch size, buffer, model, exploration

INFERENCE 
(test) 

EXPERIMENT HANDLER 
simulator# drl-torch
