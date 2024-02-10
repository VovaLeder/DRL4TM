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

GAME_SPEED = 15 # default = 1

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
        time.sleep(0.15)
        self.interface.interface.set_speed(GAME_SPEED)
        self.interface.interface.prevent_simulation_finish()
        self.saved_state = np.array(self.interface.get_state())

        # self.simthread = ThreadedClient()
        self.total_reward = 0.0
        self.n_steps = 0
        self.max_steps = 2000 / GAME_SPEED
        self.command_frequency = (1.01e-2) / GAME_SPEED
        self.last_action = None
        self.low_speed_steps = 0

        # PrevStepValues

        self.previous_distance_to_curve = 0
        self.previous_curve_direction = 0

    def action_to_command(self, action):
        gas, braking, left, right = action
        if (left == right):
            left = right = 0
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
        self.saved_state = np.array(self.interface.get_state())

        # print(f'action: {action}')
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
        time.sleep(self.command_frequency)
        return self.observation, self.reward, done, info

    def render(self):
        pass
        # print(f"total reward: {self.total_reward}")
    
    def reset(self):
        print("reset")

        print(f"total_reward: {round(self.total_reward, 3)}")
        print(f"previous_distance_to_curve: {round(self.previous_distance_to_curve, 3)}")

        self.total_reward = 0.0
        self.n_steps = 0
        self.time = 0
        self.last_action = None
        self.low_speed_steps = 0
        self.previous_distance_to_curve = 0
        self.previous_curve_direction = 0
        self._restart_race()
        print("reset done\n")
        # time.sleep(1.5 / GAME_SPEED)

        return self.observation
    
    @property
    def state(self):
        return self.saved_state

    @property
    def observation(self):
        return self.saved_state

    @property
    def reward(self):
        cur_state = self.state
        if (LEVEL == 0):
            reward = 0

            speed = cur_state[0]

            # print(f"speed: {speed}")
            # print(f"state: {cur_state}")
            if (speed > 0.5):
                reward += speed
            elif (speed > 0.3):
                reward += speed / 2 
            elif (speed > 0.2):
                reward += speed / 3
            elif (speed > 0.1):
                reward += speed / 5
            elif (speed > -0.05):
                reward += speed / 10
            else:
                reward += speed * 5
            
            if (self.previous_distance_to_curve != 0):
                if (self.previous_curve_direction - cur_state[5] == 0):
                    if (self.previous_distance_to_curve - cur_state[4] > 0):
                        reward += (self.previous_distance_to_curve - cur_state[4]) * 50
                    else:
                        reward += (self.previous_distance_to_curve - cur_state[4]) * 150
                else:
                    reward += 20

            self.previous_distance_to_curve = cur_state[4]
            self.previous_curve_direction = cur_state[5]

            reward += (0.51 - abs(cur_state[3])) / 20

            # reward += (0.85 - cur_state[4]) * 15
            if (cur_state[4] > 0.87):
                reward -= 100
            if (cur_state[4] < 0.1):
                reward += 1000

            # print('reward: ' + reward)
            return reward
