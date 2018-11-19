import math
import random
import os 

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical

import numpy as np

from utils.logger import setup_logger
from tensorboardX import SummaryWriter
from tqdm import tqdm

from datetime import datetime

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

class QNetwork(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_size, init_w=3e-3):
        super(QNetwork, self).__init__()
        
        self.linear1 = nn.Linear(num_inputs + num_actions, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, 1)
        
        self.linear3.weight.data.uniform_(-init_w, init_w)
        self.linear3.bias.data.uniform_(-init_w, init_w)

        self.to(device)
        
    def forward(self, state, action):
        x = torch.cat([state, action], 1)
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x

class ValueNetwork(nn.Module):
    def __init__(self, num_inputs, hidden_size, init_w=3e-3):
        super(ValueNetwork, self).__init__()
        
        self.linear1 = nn.Linear(num_inputs, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, 1)
        
        self.linear3.weight.data.uniform_(-init_w, init_w)
        self.linear3.bias.data.uniform_(-init_w, init_w)
        
    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x
    

class PolicyNetwork(nn.Module): #discrete
    def __init__(self, num_inputs, num_actions, hidden_size, init_w=3e-3):
        super(PolicyNetwork, self).__init__()
        
        self.linear1 = nn.Linear(num_inputs, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, num_actions)
        
        self.linear3.weight.data.uniform_(-init_w, init_w)
        self.linear3.bias.data.uniform_(-init_w, init_w)

        self.softmax = nn.Softmax(dim=1)

        self.to(device)
        
    def forward(self, state):
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))
        x = self.softmax(self.linear3(x))
        return x

class A2C(nn.Module):
    def __init__(self, state_dim, action_dim, 
        hidden_size=256, gamma=0.99, 
        optimiser="Adam", value_lr=1e-3,
        policy_lr=1e-4, load_dir="", conv=False, debug=False, 
        output_dir="", write=True, save=True, test_every=1000, test_only=False):
        super(A2C, self).__init__()
        if test_every:
            self.test_every = test_every

        self.save = save
        self.write = write

        self.gamma = gamma
        self.critic = ValueNetwork(state_dim, hidden_size)
        self.actor = PolicyNetwork(state_dim, action_dim, hidden_size)

        if load_dir:
            self.load_model(load_dir)

        self.test_only =test_only
        if not self.test_only:
            self.init_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = os.path.join(output_dir, self.init_time)
            self.ensure(output_dir)
            if self.write:
                self.writer = SummaryWriter(log_dir=self.output_dir)
                #self.dummy_input = torch.autograd.Variable(torch.rand(1, state_dim))
                #self.writer.add_graph(self.critic, self.dummy_input)
                #self.writer.add_graph(self.actor, self.dummy_input)
                #self.writer.add_graph(self, (self.dummy_input,))
                #torch.jit.get_trace_graph(self, self.dummy_input)
            optimiser_ = getattr(optim, optimiser)

            #self.value_optimizer = optimiser_(self.critic.parameters(), lr=value_lr)
            #self.policy_optimizer = optimiser_(self.actor.parameters(), lr=policy_lr)
            self.value_optimizer = optimiser_(self.critic.parameters(), lr=value_lr)
            self.policy_optimizer = optimiser_(self.actor.parameters(), lr=policy_lr)

        
    def forward(self, x): #x is the state, a 1-dim state  
        value = self.critic(x)
        probs = self.actor(x)
        dist  = Categorical(probs)
        return dist, value

    def compute_returns(self, next_value, rewards, masks):
        R = next_value
        returns = []
        for step in reversed(range(len(rewards))):
            R = rewards[step] + self.gamma * R * masks[step]
            returns.insert(0, R)
        return returns

    def trainer(self, environment, max_episodes, num_steps=5):

        state = environment.reset()
        test_rewards=[]

        for episode in tqdm(range(max_episodes)):

            log_probs = []
            values    = []
            rewards   = []
            masks     = []
            entropy = 0

            for _ in range(num_steps):
                state = torch.FloatTensor(state).to(device)
                dist, value = self.forward(state)

                action = dist.sample()
                next_state, reward, done, _ = environment.step(action.cpu().numpy())

                log_prob = dist.log_prob(action)
                entropy += dist.entropy().mean()
                
                log_probs.append(log_prob)
                values.append(value)
                rewards.append(torch.FloatTensor(reward).unsqueeze(1).to(device))
                masks.append(torch.FloatTensor(1 - done).unsqueeze(1).to(device))
                
                state = next_state
                episode += 1
                
                if not (episode % self.test_every) and self.test_every:
                    test_reward = np.mean([self.test(environment) for _ in range(10)])
                    test_rewards.append(test_reward)
                    self.writer.add_scalar("test/reward", np.mean(test_reward), episode)
                    if self.save:
                        self.save_model(self.save_output_dir(episode))

            next_state = torch.FloatTensor(next_state).to(device)
            _, next_value = self.forward(next_state)
            returns = self.compute_returns(next_value, rewards, masks)
            
            
            log_probs = torch.cat(log_probs)
            returns   = torch.cat(returns).detach()
            values    = torch.cat(values)
            #print(values.mean())
            self.writer.add_scalar("train/mean_return", np.mean([r for r in returns]), episode)
            self.writer.add_scalar("train/mean_value_function", values.mean().data, episode)

            advantage = returns - values
            
            self.writer.add_scalar("train/mean_advantage", advantage.mean().data, episode)
            actor_loss  = -(log_probs * advantage.detach()).mean()
            self.writer.add_scalar("train/actor_loss", actor_loss.data, episode)
            critic_loss = advantage.pow(2).mean()
            self.writer.add_scalar("train/critic_loss", critic_loss.data, episode)

            loss = actor_loss + 0.5 * critic_loss - 0.001 * entropy
            self.writer.add_scalar("train/loss", loss.data, episode)
            #self.writer.add_scalars("train/losses", self.unwrapper(loss), episode)
            #self.writer.add_scalars("train/entropies", self.unwrapper(entropy), episode)

            self.value_optimizer.zero_grad()
            self.policy_optimizer.zero_grad()
            loss.backward()
            self.value_optimizer.step()
            self.policy_optimizer.step()

        self.save_model(self.save_output_dir("final"))

    def test(self, test_env=None, iterations=1):

        try:
            environment = self.test_env()
        except:
            environment = test_env()

        returns = []
        for _ in range(iterations):
            state = environment.reset()
            done = False
            total_reward = 0
            while not done:
                state = torch.FloatTensor(state).unsqueeze(0).to(device)
                dist, _ = self.forward(state)
                if self.test_only:
                    environment.render()
                next_state, reward, done, _ = environment.step(dist.sample().cpu().numpy()[0])
                state = next_state
                total_reward += reward
            returns.append(total_reward)
        if self.test_only:
            environment.close()
        return np.mean(returns)

    def save_model(self, output_dir):
        print("Saving the actor-critic model")
        torch.save(
            self.state_dict(),
            '{}/a2c_n.pkl'.format(output_dir)
        )


    def save_output_dir(self, episode):
        output_dir = os.path.join(
            self.output_dir, str(episode))
        self.ensure(output_dir)
        
        return output_dir

    def load_model(self, load_dir):
        checkpoint = torch.load(os.path.join(load_dir, "a2c_n.pkl"))
        self.load_state_dict(checkpoint)
        #checkpoint_critic = torch.load(os.path.join(load_dir, "critic.pkl"))
        #self.critic.load_state_dict(checkpoint_critic)

    def unwrapper(self, tensor):
        return dict((str(i), t) for i, t in enumerate(tensor))

    def ensure(self, _dir):
        if not os.path.exists(_dir):
            os.makedirs(_dir)

