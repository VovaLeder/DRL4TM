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

GAME_SPEED = 1 # default = 1
COMMAND_SPEED = 0.05

class TMEnv(Env):
    def __init__(self):
        self.actual_max_distance = 1
        self.actual_max_reward = 0

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
        self.max_steps = 500 / GAME_SPEED
        self.command_frequency = 0.05 / GAME_SPEED

        # PrevStepValues
        
        self.last_action = None
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

    def step(self, input_action):

        action_correspondance = {
            i + 2 * j + 4 * k + 8 * l: [i, j, k, l]
            for i in range(2)
            for j in range(2)
            for k in range(2)
            for l in range(2)
        }

        action = action_correspondance[input_action.item()]
        

        self.last_action = action
        self.saved_state = np.array(self.interface.get_state())

        # print(f'action: {action}')
        self.last_action = action

        self.action_to_command(action)

        done = False
        if (self.n_steps >= self.max_steps or self.total_reward < -100 or self.total_reward > 500):
            done = True
            if (self.total_reward > 200):
                print("yay!")
            elif (self.total_reward < -100):
                print("meh :(")

        cur_reward = self.reward
        self.total_reward += cur_reward
        self.n_steps += 1
        info = {}
        time.sleep(self.command_frequency)
        return self.observation, cur_reward, done, info

    def render(self):
        pass
        # print(f"total reward: {self.total_reward}")
    
    def reset(self):
        # print("reset")

        # print(f"total_reward: {round(self.total_reward, 3)}")
        # print(f"previous_distance_to_curve: {round(self.previous_distance_to_curve, 3)}")

        print(f"{time.strftime('%H:%M:%S', time.localtime())} | total_reward: {self.total_reward}")
        print()
        if (self.total_reward > self.actual_max_reward):
            self.actual_max_reward = self.total_reward
            print(f"{time.strftime('%H:%M:%S', time.localtime())} | actual_max_reward: {self.actual_max_reward}")
        
        if (self.previous_distance_to_curve < self.actual_max_distance):
            self.actual_max_distance = self.previous_distance_to_curve
            print(f"{time.strftime('%H:%M:%S', time.localtime())} | actual_max_distance: {self.actual_max_distance}")


        self.total_reward = 0.0
        self.n_steps = 0
        self.time = 0
        self.last_action = None
        self.previous_distance_to_curve = 0
        self.previous_curve_direction = 0
        self._restart_race()
        # print("reset done\n")
        # time.sleep(1.5 / GAME_SPEED)

        return self.observation
    
    @property
    def state(self):
        return self.interface.client.sim_state

    @property
    def observation(self):
        return self.saved_state

    @property
    def reward(self):
        cur_state = self.observation
        if (LEVEL == 0):
            reward = 0

            speed = cur_state[0]

            # print(f"speed: {speed}")
            # print(f"state: {cur_state}")
            if (speed > 0.5):
                reward += speed
            elif (speed > 0.3):
                reward += speed / 1.1 
            elif (speed > 0.2):
                reward += speed / 1.2
            elif (speed > 0.1):
                reward += speed / 1.3
            elif (speed > -0.05):
                reward += speed / 1.5
            else:
                reward += speed * 5
            
            if (self.previous_distance_to_curve != 0):
                if (self.previous_curve_direction == cur_state[5]):
                    if (self.previous_distance_to_curve - cur_state[4] > 0):
                        reward += (self.previous_distance_to_curve - cur_state[4]) * 50
                    else:
                        reward += (self.previous_distance_to_curve - cur_state[4]) * 250
                else:
                    reward += 5

            self.previous_distance_to_curve = cur_state[4]
            self.previous_curve_direction = cur_state[5]

            bad_angle_c = 0.4 - abs(cur_state[3])
            if (bad_angle_c <= 0):
                reward += bad_angle_c * 5

            # if (self.last_action[0]):
            #     reward += 5
            # if (self.last_action[1]):
            #     reward -= 2
            # if (self.last_action[2]):
            #     reward -= 2
            # if (self.last_action[3]):
            #     reward -= 2

            # reward += (0.85 - cur_state[4]) * 15
            if (cur_state[4] > 0.855):
                reward -= 70
            if (cur_state[4] < 0.1):
                reward += 400

            
        elif (LEVEL == 1):
            reward = 0

            speed = cur_state[0]

            # print(f"speed: {speed}")
            # print(f"state: {cur_state}")
            if (speed > 0.5):
                reward += speed / 2
            elif (speed > 0.3):
                reward += speed / 2.2 
            elif (speed > 0.2):
                reward += speed / 3.3
            elif (speed > 0.1):
                reward += speed / 4.4
            elif (speed > -0.05):
                reward += speed / 5.5
            else:
                reward += speed
            
            if (self.previous_distance_to_curve != 0):
                if (self.previous_curve_direction == cur_state[5]):
                    if (self.previous_distance_to_curve - cur_state[4] > 0):
                        reward += (self.previous_distance_to_curve - cur_state[4]) * 50
                    else:
                        reward += (self.previous_distance_to_curve - cur_state[4]) * 250
                else:
                    reward += 1

            self.previous_distance_to_curve = cur_state[4]
            self.previous_curve_direction = cur_state[5]

            bad_angle_c = 0.4 - abs(cur_state[3])
            if (bad_angle_c <= 0):
                reward += bad_angle_c * 20

            # if (self.last_action[0]):
            #     reward += 1
            # if (self.last_action[1]):
            #     reward -= 5
            # if (self.last_action[2]):
            #     reward -= 1
            # if (self.last_action[3]):
            #     reward -= 1

            start_fin_reward = 0
            if (cur_state[5] == 0):
                start_fin_reward += 100
            elif (self.state.dyna.current_state.position[1] < 40):
                start_fin_reward -= 70

            reward += start_fin_reward

        # print(f'reward: {reward}')
        return reward
