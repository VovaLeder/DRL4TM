from gym import Env
from gym.spaces import Discrete, Box, Tuple
import numpy as np

# gas, break, steer
ACTION_SPACE = Tuple((Discrete(2), Discrete(2), Box(-1, 1, (1,))))
OBSERVATION_SPACE = Box(-1, 1, (8,))

class TMEnv(Env):
    def __init__(self):
        self.action_space = ACTION_SPACE
        self.observation_space = OBSERVATION_SPACE

        
    def step(self, action):
        pass
        # return self.state, reward, done, info

    def render(self):
        pass
    
    def reset(self):
        pass
        # return self.state