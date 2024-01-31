from abc import ABC
import numpy as np

from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def act(self, observation):
        raise NotImplementedError

class RandomArrowsAgent(Agent):
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation):
        action = self.action_space.sample()

        return action
