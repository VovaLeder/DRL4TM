import time
import numpy as np
import torch
import torch.nn as nn
from agent import Agent


class DQN(nn.Module):
    def __init__(self, input_size, output_size, mid_size=32, p=0.5) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_size, mid_size)
        self.fc2 = nn.Linear(mid_size, output_size)
        self.dropout = nn.Dropout(p=p)

    def forward(self, observation):
        x = torch.Tensor(observation).to("cuda")
        x = self.fc1(x)
        x = nn.ReLU()(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class EpsilonGreedyDQN(Agent):
    def __init__(self, input_size, device, eps=1e-3) -> None:
        super().__init__()
        self.device = device
        self.eps_start = 0.9
        self.eps_end = eps
        self.eps_decay = 200
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
    input_size = 6
    device = "cuda"
    time.sleep(0.5)
    agent = EpsilonGreedyDQN(input_size, device)

    for step in range(10):
        print('wrong file')
        # print(agent.epsilon())