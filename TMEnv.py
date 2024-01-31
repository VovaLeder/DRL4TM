from gym import Env
from gym.spaces import MultiBinary, Box
import numpy as np

import time
from GameLaunch import GameLauncher
from TMInterface import SimStateInterface
from constants import LEVEL

# gas, break, steer
ACTION_SPACE = MultiBinary((4,))
OBSERVATION_SPACE = Box(-1, 1, (6,))

class TMEnv(Env):
    def __init__(self):
        self.action_space = ACTION_SPACE
        self.observation_space = OBSERVATION_SPACE

        game_launcher = GameLauncher()
        if not game_launcher.game_started:
            game_launcher.start_game()
            print("game started")
            input("press enter when game is ready")
            time.sleep(4)
        self.interface = SimStateInterface()
        time.sleep(0.3)
        self.interface.interface.prevent_simulation_finish()

        # self.simthread = ThreadedClient()
        self.total_reward = 0.0
        self.n_steps = 0
        self.max_steps = 250
        self.command_frequency = 50
        self.last_action = None
        self.low_speed_steps = 0

    def action_to_command(self, action):
        gas, braking, left, right = action
        actions = {
            'accelerate': gas,
            'brake': braking,
            'left': left,
            'right': right
        }
        # print(f'actions: {actions}')
        self.interface.set_actions(**actions)

    def _restart_race(self):
        self.interface.reset()

    def step(self, action):
        print(f'action: {action}')
        self.last_action = action

        self.action_to_command(action)
        done = (
            True
            if self.n_steps >= self.max_steps or self.total_reward < -60 or self.total_reward > 500
            else False
        )
        self.total_reward += self.reward
        self.n_steps += 1
        info = {}
        time.sleep(self.command_frequency * 1e-3)
        return self.observation, self.reward, done, info

    def render(self):
        print(f"total reward: {self.total_reward}")
        # print(f"speed: {self.speed}")
        # print(f"time = {self.state.time}")
    
    def reset(self):
        print("reset")
        self.total_reward = 0.0
        self.n_steps = 0
        self.time = 0
        self.last_action = None
        self.low_speed_steps = 0
        self._restart_race()
        print("reset done")
        time.sleep(0.2)

        return self.observation
    
    @property
    def state(self):
        return np.array(self.interface.get_state())

    @property
    def observation(self):
        return self.state

    @property
    def reward(self):
        cur_state = self.state
        if (LEVEL == 0):
            reward = 0

            speed = cur_state[0]

            # print(f"speed: {speed}")
            # print(f"state: {cur_state}")
            if (speed > 0.5):
                reward += speed * 10
            elif (speed > 0.3):
                reward += speed * 5
            elif (speed > 0.2):
                reward += speed * 2.5
            elif (speed > 0.1):
                reward += speed
            elif (speed > -0.05):
                reward += speed / 5
            else:
                reward -= 0.5
            

            # reward += (0.85 - cur_state[4]) * 15
            if (cur_state[4] > 0.87):
                reward -= 100
            if (cur_state[4] < 0.01):
                reward += 1000

            # print(reward)
            return reward
