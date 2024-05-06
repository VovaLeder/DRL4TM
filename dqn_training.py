import torch
import torch.optim as optim
import torch.nn as nn
from TMEnv import TMEnv
from training_utils import Buffer, Transition, play_episode
from dqn_agent import EpsilonGreedyDQN
import numpy as np
from os import path
import datetime

base_path = path.join(path.curdir, 'model_dicts')

class DQN_trainer:
    def __init__(self, save_path, batch_size=32, N_epochs=100, load_path=None):
        self.N_epochs = N_epochs 
        self.GAMMA = 0.999
        self.target_update = 3
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.buffer = Buffer(capacity=10000)
        self.env = TMEnv()
        self.agent = EpsilonGreedyDQN(
            input_size=self.env.observation_space.shape[0], device=self.device
        )
        self.optimizer = optim.Adam(self.agent.policy.parameters(), lr=0.001)
        self.loss = nn.SmoothL1Loss()
        self.fill_buffer()

        self.save_path = save_path
        self.load_path = load_path

    def fill_buffer(self):
        while len(self.buffer) < self.batch_size:
            episode = play_episode(self.agent, self.env)
            episode = filter(lambda transition: not transition.done, episode)
            self.buffer.append_multiple(list(episode))

    def optimize_step(self):
        batch = self.buffer.sample(self.batch_size)
        inv_map = {tuple(v): k for k, v in self.agent.action_correspondance.items()}
        state_batch = torch.tensor(
            np.array([t.state for t in batch]), dtype=torch.float
        ).to(self.device)
        action_batch = torch.tensor(
            np.array([inv_map[tuple(t.action)] for t in batch]), dtype=torch.float
        ).to(self.device)
        reward_batch = torch.tensor(
            np.array([t.reward for t in batch]), dtype=torch.float
        ).to(self.device)
        next_state_batch = torch.tensor(
            np.array([t.next_state for t in batch]), dtype=torch.float
        ).to(self.device)
        state_action_values = (
            self.agent.policy(state_batch)
            .gather(1, action_batch.unsqueeze(1).type(torch.int64))
            .squeeze(1)
        )
        # print(state_action_values.shape)
        next_state_values = self.agent.target(next_state_batch).max(1)[0].detach()
        # print(next_state_values.shape)
        # print(reward_batch.shape)
        expected_action_values = (next_state_values * self.GAMMA) + reward_batch
        # print(state_action_values.shape, expected_action_values.shape)
        loss = self.loss(state_action_values, expected_action_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def train(self):
        if (self.load_path is not None):
            self.agent.target.load_state_dict(torch.load(self.load_path))
        for epoch in range(self.N_epochs):
            self.env.reset()
            episode = []
            observation = self.env.reset()
            done = False
            step = 0
            while not done:
                prev_obs = observation
                action = self.agent.act(observation)
                # print(action)
                observation, reward, done, info = self.env.step(action)
                transition = Transition(prev_obs, action, observation, reward, done)
                episode.append(transition)
                step += 1
                self.env.render()
                self.optimize_step()

            self.buffer.append_multiple(list(episode))
            if epoch % self.target_update == 0:
                print(f"EPOCH: {epoch}")
                self.agent.target.load_state_dict(self.agent.policy.state_dict())
                torch.save(self.agent.policy.state_dict(), self.save_path)


if __name__ == "__main__":
    save_path = path.join(base_path, str(datetime.datetime.now()).replace('.', '').replace('-', '').replace(':', '').replace(' ', ''))
    load_path = path.join(base_path, '1_straght')
    # load_path = None
    trainer = DQN_trainer(N_epochs=3000, save_path=save_path, load_path=None)
    trainer.train()