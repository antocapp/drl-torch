#implement here Environment function
import numpy as np
from random import random
import gym
#import gym_forex 
#Create different plants for every system to train the agent on 

class Plant:
    def __init__(self):
        self.data = [] #anything useful to reward 
        self.state = None
        pass

    def __call__(self, state, action):
        return self.equation(state, action)
    
    def equation(self, state, action):
        #perform operation on action
        next_state = [2]
        if random() > 0.8:
            done = True
        else:
            done = False
        return next_state, done

    def reward(self, next_state, action):
        #data can be any other factor unknown to others, such as noise or possible occlusions
        #can also be anything related to the state or intrinsic state of the system 
        reward = sum(self.data)+ sum(self.state) + sum(next_state) + sum(action)
        reward += 10.
        self.state = next_state
        return reward


class Environment(object):
    def __init__(self, plant=Plant):
        self.observation_space = np.zeros([32], dtype=float)
        self.action_space = 3
        self.plant = plant()

    def step(self, action):
        #receive actions and returns next state and reward

        next_state, done = self.plant(action)
        reward = self.plant.reward(next_state, action)
        info = {}
        return next_state, reward, done, info

    def reset(self):
        #return initial state S0
        pass

#GYM environment#
def CartPole():
    def _thunk():
        env =  gym.make("CartPole-v0")
        return env
    return _thunk
