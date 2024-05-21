from pygbx import Gbx, GbxType

level_name = "Level2Big"

g = Gbx(f'C:\\Users\\vovaleder\\Documents\\TmForever\\Tracks\Challenges\\My Challenges\\{level_name}.Challenge.Gbx')
challenges = g.get_classes_by_ids([GbxType.CHALLENGE, GbxType.CHALLENGE_OLD])
if not challenges:
    quit()

challenge = challenges[0]
for block in challenge.blocks:
    # print(block)
    if (block.flags != 3):
        print(f'[{block.position.x}, {block.position.y}, {block.position.z}],')