from abc import ABC
import numpy as np

from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def act(self, observation):
        raise NotImplementedError

class RandomGamepadAgent(Agent):
    def act(self, observation):
        return np.random.uniform(-1, 1, size=(3,))
