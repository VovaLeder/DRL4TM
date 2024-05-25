from os import path

import torch

base_path = path.join(path.curdir, 'model_dicts')
load_path = path.join(base_path, 'm1t6_192_192', '20240525091044755124.tar')

# 448072 487773 186833

checkpoint = torch.load(load_path)
print(checkpoint['steps_done'])