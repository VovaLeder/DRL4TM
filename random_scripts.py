from os import path

import torch

base_path = path.join(path.curdir, 'model_dicts')
load_path = path.join(base_path, 'm1t10_128_128', '20240529021822873176.tar')

# 448072 487773 186833

checkpoint = torch.load(load_path)
print(checkpoint['steps_done'])