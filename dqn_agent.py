import time
import numpy as np
import torch
import torch.nn as nn
from agent import Agent


class DQN(nn.Module):
    def __init__(self, input_size, output_size, mid_size=48, p=0.2) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_size, mid_size)
        self.fc2 = nn.Linear(mid_size, mid_size * 2)
        self.fc3 = nn.Linear(mid_size * 2, mid_size)
        self.fc4 = nn.Linear(mid_size, output_size)
        self.dropout = nn.Dropout(p=p)

    def forward(self, observation):
        x = torch.Tensor(observation).to("cuda")
        x = self.fc1(x)
        x = nn.ReLU()(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = nn.ReLU()(x)
        x = self.dropout(x)
        x = self.fc3(x)
        x = nn.ReLU()(x)
        x = self.dropout(x)
        x = self.fc4(x)
        return x


class EpsilonGreedyDQN(Agent):
    def __init__(self, input_size, device) -> None:
        super().__init__()
        self.device = device
        self.action_correspondance = {
            i + 2 * j + 4 * k + 8 * l: [i, j, k, l]
            for i in range(2)
            for j in range(2)
            for k in range(2)
            for l in range(2)
        }
        self.policy = DQN(input_size, len(self.action_correspondance))
        self.target = DQN(input_size, len(self.action_correspondance))
        self.policy.to(self.device)
        self.target.to(self.device)
        self.step = 0

    def act(self, observation):
        self.step += 1
        if np.random.rand() < 0.95: # ?
            smth = self.policy(observation).detach().cpu().numpy()
            # print(f'step: {self.step}. smth: {smth}')
            return self.action_correspondance[
                np.argmax(smth)
            ]
        
        return self.action_correspondance[
            np.random.randint(0, len(self.action_correspondance))
        ]


if __name__ == "__main__":
    print('wrong file')