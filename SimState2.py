from math import atan2, cos, pi, sin


TURNS = [
    # || 484.4 - 496 - 507.6 ||
    # 436.8 468.8 500.8
    # y = 161.35
    # z12 = 395.2
    # z13 = 427.2
    # x18 = 592
    
    # -1 - L   1 - R

    [18, 20, 12, 0], # 592 395.2
    [18, 20, 15, 1], # r
    # 564.8 496
    [16, 20, 15, 1], # r
    # 528 427.2
    [16, 20, 12, -1], # l
    [13, 20, 12, -1], # l
    [13, 20, 15, 1], # r
    [12, 20, 15, -1], # l
    [12, 20, 17, -1], # l
    [14, 20, 17, -1], # l
    [14, 20, 16, 1], # r 
    [15, 20, 16, 1], # r
    [15, 20, 21, -1], # l
    [16, 20, 21, -1], # l
    [16, 20, 16, 1], # r 
    [17, 20, 16, 1], # r
    [17, 20, 17, -1], # l
    [19, 20, 17, -1], # l
    [19, 20, 12, 0],
]

    
class SimState2():
    def __init__(self) -> None:
        self.linear_speed = 0
        self.angular_speed = 0
        self.distance_to_centerline = 0
        self.angle_to_centerline = 0

        self.next_curve_distance = 0
        self.next_curve_direction = 0

        self.next_curve_distance2 = 0 
        self.next_curve_direction2 = 0 

        self.next_curve_distance3 = 0
        self.next_curve_direction3 = 0

        self.cur = 0

    def get_info(self, pos, rot, linear_speed, angular_speed):
        self.linear_speed = linear_speed
        self.angular_speed = angular_speed

        prev_turn_index = None

        for turn_index, turn in enumerate(TURNS):
            next_turn = TURNS[turn_index + 1] if len(TURNS) - 1 > turn_index else None
            if (next_turn == None):
                break
            if (turn[0] == next_turn[0]):
                if (turn[2] < next_turn[2]):
                    if (pos[0] >= turn[0] * 32 and pos[0] <= (turn[0] + 1) * 32 and pos[2] >= turn[2] * 32 and pos[2] <= (next_turn[2] + 1) * 32):
                        prev_turn_index = turn_index
                else:
                    if (pos[0] >= turn[0] * 32 and pos[0] <= (turn[0] + 1) * 32 and pos[2] >= next_turn[2] * 32 and pos[2] <= (turn[2] + 1) * 32):
                        prev_turn_index = turn_index
            else:
                if (turn[0] < next_turn[0]):
                    if (pos[2] >= turn[2] * 32 and pos[2] <= (turn[2] + 1) * 32 and pos[0] >= turn[0] * 32 and pos[0] <= (next_turn[0] + 1) * 32):
                        prev_turn_index = turn_index
                else:
                    if (pos[2] >= turn[2] * 32 and pos[2] <= (turn[2] + 1) * 32 and pos[0] >= next_turn[0] * 32 and pos[0] <= (turn[0] + 1) * 32):
                        prev_turn_index = turn_index

        onFinishBlock = False
        if (pos[2] >= TURNS[-1][2] * 32 and pos[2] <= (TURNS[-1][2] + 1) * 32 and pos[0] >= TURNS[-1][0] * 32 and pos[0] <= (TURNS[-1][0] + 1) * 32):
            onFinishBlock = True

        if (prev_turn_index == None and not onFinishBlock):
            return
        
        self.cur = prev_turn_index

        turn = TURNS[prev_turn_index] if not onFinishBlock else TURNS[-2]
        next_turn = TURNS[prev_turn_index + 1] if not onFinishBlock else TURNS[-1]
        next_turn2 = TURNS[prev_turn_index + 2] if (len(TURNS) - 2 > prev_turn_index) else None
        next_turn3 = TURNS[prev_turn_index + 3] if (len(TURNS) - 3 > prev_turn_index) else None

        self.next_curve_direction = next_turn[3]
        self.next_curve_direction2 = next_turn2[3] if next_turn2 != None else 0
        self.next_curve_direction3 = next_turn3[3] if next_turn3 != None else 0

        self.next_curve_distance = 700
        self.next_curve_distance2 = 700
        self.next_curve_distance3 = 700

        if (turn[0] == next_turn[0]):
            if (turn[2] < next_turn[2]):
                self.next_curve_distance = (next_turn[2] * 32 - pos[2]) if ((not onFinishBlock) and next_turn[3] != 0) else 700
                self.distance_to_centerline = turn[0] * 32 + 16 - pos[0]
                self.angle_to_centerline = - atan2(rot[0, 2], rot[0, 0])
            else:
                self.next_curve_distance = (pos[2] - next_turn[2] * 32 - 32) if ((not onFinishBlock) and next_turn[3] != 0) else 700
                self.distance_to_centerline = pos[0] - turn[0] * 32 - 16
                self.angle_to_centerline = - atan2(-rot[0, 2], -rot[0, 0])
        else:
            if (turn[0] < next_turn[0]):
                self.next_curve_distance = (next_turn[0] * 32 - pos[0]) if ((not onFinishBlock) and next_turn[3] != 0) else 700
                self.distance_to_centerline = pos[2] - turn[2] * 32 - 16
                self.angle_to_centerline = atan2(rot[0, 0], rot[0, 2])
            else:
                self.next_curve_distance = (pos[0] - next_turn[0] * 32 - 32) if ((not onFinishBlock) and next_turn[3] != 0) else 700
                self.distance_to_centerline = turn[2] * 32 + 16 - pos[2]
                self.angle_to_centerline = atan2(-rot[0, 0], -rot[0, 2])

        if (next_turn2 != None):
            if (next_turn[0] == next_turn2[0]):
                self.next_curve_distance2 = ((abs(next_turn2[2] - next_turn[2]) - 0.5) * 32) if next_turn2[3] != 0 else 700
            else:
                self.next_curve_distance2 = (abs(next_turn2[0] - next_turn[0]) - 0.5) * 32 if next_turn2[3] != 0 else 700

            if (next_turn3 != None):
                if (next_turn2[0] == next_turn3[0]):
                    self.next_curve_distance3 = (abs(next_turn3[2] - next_turn2[2]) - 0.5) * 32 if next_turn3[3] != 0 else 700
                else:
                    self.next_curve_distance3 = (abs(next_turn3[0] - next_turn2[0]) - 0.5) * 32 if next_turn3[3] != 0 else 700



    def normalize(self):
        self.linear_speed = self.linear_speed / 840
        self.angular_speed = self.angular_speed / 30
        self.distance_to_centerline = self.distance_to_centerline / 12
        self.angle_to_centerline = self.angle_to_centerline / pi
        self.next_curve_distance = self.next_curve_distance / 700
        self.next_curve_distance2 = self.next_curve_distance2 / 700
        self.next_curve_distance3 = self.next_curve_distance3 / 700

    def get_state(self):
        return [
            self.linear_speed,
            self.angular_speed,
            self.distance_to_centerline,
            self.angle_to_centerline,

            self.next_curve_distance,
            self.next_curve_direction,
            self.next_curve_distance2,
            self.next_curve_direction2,
            self.next_curve_distance3,
            self.next_curve_direction3,
        ]
    
    def __str__(self):
        return f"""
        SimState2
        lin_speed: {self.linear_speed}
        ang_speed: {self.angular_speed}
        dist_to_center: {self.distance_to_centerline}
        angle_to_centerline: {self.angle_to_centerline}
        next_curve_dist: {self.next_curve_distance}
        next_curve_dir: {self.next_curve_direction}
        next_curve_dist2: {self.next_curve_distance2}
        next_curve_dir2: {self.next_curve_direction2}
        next_curve_dist3: {self.next_curve_distance3}
        next_curve_dir3: {self.next_curve_direction3}
        """