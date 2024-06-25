import datetime
import math
from os import path
import os
import random
from itertools import count
import time

import torch
import torch.nn as nn
import torch.optim as optim

from dqn import DQN
from replay_memory import ReplayMemory, Transition
from hyperparameters import *
from TMEnv import TMEnv

def get_str_time():
    return str(datetime.datetime.now()).replace('.', '').replace('-', '').replace(':', '').replace(' ', '')

base_path = path.join(path.curdir, 'model_dicts')

episode_durations = []

env = TMEnv()

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    
# Training utils

# Get number of actions from
n_actions = 16

# Get the number of state observations
state = env.reset()
n_observations = len(state)

policy_net = DQN(n_observations, n_actions).to(device) 
target_net = DQN(n_observations, n_actions).to(device)

target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)
memory = ReplayMemory(15000)


steps_done = 0


def select_action(state, eval_mode = True):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if ((sample > eps_threshold) or eval_mode):
        with torch.no_grad():
            # t.max(1) will return the largest column value of each row.
            # second column on max result is index of where max element was
            # found, so we pick action with the larger expected reward.
            return policy_net(state).max(1).indices.view(1, 1)
    else:
        return torch.tensor(
            [[random.randint(0, n_actions - 1)]], device = device, dtype=torch.long
        )
    

# Training Loop 

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))
    non_final_mask = torch.tensor(
        tuple(map(lambda s: s is not None,
                batch.next_state)),
        device=device,
        dtype=torch.bool
    )
    non_final_next_states = torch.cat(
        [s for s in batch.next_state
            if s is not None]
        )
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    state_action_values = policy_net(state_batch).gather(1, action_batch)

    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(
            non_final_next_states
        ).max(1).values

    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()

def train(save_path, load_path=None, par_steps_done=None, eval=False):
    global target_net, policy_net, optimizer, steps_done

    steps_done = 0
    if (load_path != None):
        checkpoint = torch.load(load_path)
        target_net.load_state_dict(checkpoint['target_net_state_dict'])
        policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        memory._full_set(checkpoint['memory'])
        if (par_steps_done == None):
            steps_done = checkpoint['steps_done']
        else:
            steps_done = par_steps_done

    target_net.train()
    policy_net.train()

    for i_episode in count():
        # print(f'i_episode: {i_episode}')
        # Initialize the environment and get its state

        if (i_episode % 10 == 0):
            state = env.reset()
            os.makedirs(save_path, exist_ok=True)
            torch.save({
                'policy_net_state_dict': policy_net.state_dict(),
                'target_net_state_dict': target_net.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'memory': memory._full_get(),
                'steps_done': steps_done
            }, path.join(save_path, get_str_time() + '.tar'))
            time.sleep(1)
        
        state = env.reset()
        state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        for t in count():
            action = select_action(state, eval_mode=eval)
            observation, reward, terminated, info = env.step(action)
            reward = torch.tensor([reward], device=device)
            done = terminated

            if terminated:
                next_state = None
            else:
                next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

            # Store the transition in memory
            memory.push(state, action, next_state, reward)

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the policy network)
            optimize_model()

            # Soft update of the target network's weights
            # θ′ ← τ θ + (1 −τ )θ′
            target_net_state_dict = target_net.state_dict()
            policy_net_state_dict = policy_net.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
            target_net.load_state_dict(target_net_state_dict)

            if done:
                episode_durations.append(t + 1)
                break

def eval(load_path):
    global target_net, policy_net, optimizer

    checkpoint = torch.load(load_path)
    target_net.load_state_dict(checkpoint['target_net_state_dict'])
    policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    target_net.eval()
    policy_net.eval()


    while (True):
        # print(f'i_episode: {i_episode}')
        # Initialize the environment and get its state
        state = env.reset()
        state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        for t in count():
            action = select_action(state)
            observation, reward, terminated, info = env.step(action)
            reward = torch.tensor([reward], device=device)
            done = terminated

            if terminated:
                next_state = None
            else:
                next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

            # Move to the next state
            state = next_state

            if done:
                episode_durations.append(t + 1)
                break

if __name__ == '__main__':
    save_path = path.join(base_path, 'm1t3_128_128')
    load_path = path.join(base_path, 'm1t20_128_128_could_be_beautifuk', '20240608061918710111.tar')

    # train(save_path)
    # train(save_path, load_path=load_path, eval=True)
    # train(save_path, load_path=load_path, par_steps_done=6500)
    eval(load_path=load_path)
