from itertools import count
from TMEnv import TMEnv


env = TMEnv()

for i_episode in range(100):

  state = env.reset()

  for t in count():
    observation, reward, terminated, info = env._manual_step()
    if terminated:
      break