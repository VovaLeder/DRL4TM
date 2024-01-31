from gym import Env
from gym.spaces import Box
import numpy as np

import time
from GameLaunch import GameLauncher
from TMInterface import SimStateInterface

# gas, break, steer
ACTION_SPACE = Box(-1, 1, (3,))
OBSERVATION_SPACE = Box(-0.5, 1, (6,))

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

        # self.simthread = ThreadedClient()
        self.total_reward = 0.0
        self.n_steps = 0
        self.max_steps = 1000
        self.command_frequency = 50
        self.last_action = None
        self.low_speed_steps = 0

    def action_to_command(self, action):
        gas, breaking, steer = action
        actions = {
            'gas': int(gas*65536),
            'break': breaking >= 0.1,
            'steer': int(steer*65536),
        }
        self.interface.set_actions(**actions)

    def _restart_race(self):
        self.interface.reset()

    def step(self, action):
        self.last_action = action

        self.action_to_command(action)
        done = (
            True
            if self.n_steps >= self.max_steps or self.total_reward < -300
            else False
        )
        self.total_reward += self.reward
        self.n_steps += 1
        info = {}
        time.sleep(self.command_frequency * 10e-3)
        return self.observation, self.reward, done, info

    def render(self):
        print(f"total reward: {self.total_reward}")
        print(f"speed: {self.speed}")
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
    def speed(self):
        return self.state[0]

    @property
    def observation(self):
        return self.state

    @property
    def reward(self):
        speed = self.speed
        # if self.state.time < 3000:
        #     return 0

        speed_reward = speed / 400
        constant_reward = -0.3
        gas_reward = self.last_action[0] * 2

        # if self.last_action[0] < 0:
        #     constant_reward -= 10
        #     gas_reward = 0

        # if min(self.observation) < 0.06:
        #     constant_reward -= 100

        if 10 < speed < 100:
            speed_reward = -1
            gas_reward = 0

        elif speed < 10:
            self.low_speed_steps += 1
            speed_reward = -5 * self.low_speed_steps
            gas_reward = 0

        else:
            self.low_speed_steps = 0

        return speed_reward + constant_reward + gas_reward
