from pygbx import Gbx, GbxType

level = 0

g = Gbx(f'C:\\Users\\vovaleder\\Documents\\TmForever\\Tracks\Challenges\\My Challenges\\Level{level}Orig.Challenge.Gbx')
challenges = g.get_classes_by_ids([GbxType.CHALLENGE, GbxType.CHALLENGE_OLD])
if not challenges:
    quit()

challenge = challenges[0]
for block in challenge.blocks:
    print(block)