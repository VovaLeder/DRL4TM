from utils import get_info_from_center_line_0, get_info_from_center_line_1, normalize_info

class SimState():
    def __init__(self) -> None:
        #                     Maxes
        self.linear_speed = 0 # 240 (about 840 in TM) (about 272 actual in the zero map; 70 - first)
        self.angular_speed = 0 # Got to 30 max on grass, might want to drop or change
        self.distance_to_centerline = 0 # 14
        self.angle_to_centerline = 0 # pi
        self.next_curve_distance = 0 # pi on curves and about 0.5 on straight
        self.next_curve_direction = 0 # -1 and 1, 0 on road to fin

    def get_info_from_center_line(self, pos, rot):
        raise NotImplementedError
    def normalize(self):
        raise NotImplementedError
    def get_state(self):
        raise NotImplementedError

class SimState0(SimState):
    def __init__(self) -> None:
        super().__init__()

    def get_info_from_center_line(self, pos, rot):
        arg = get_info_from_center_line_0(pos, rot)
        self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction = arg

    def normalize(self):
        self.linear_speed, self.angular_speed, self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction = normalize_info(self)

    def get_state(self):
        return [self.linear_speed, self.angular_speed, self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction]
    
    def __str__(self):
        return f"""
        SimState0
        lin_speed: {self.linear_speed}
        ang_speed: {self.angular_speed}
        dist_to_center: {self.distance_to_centerline}
        angle_to_centerline: {self.angle_to_centerline}
        next_curve_dist: {self.next_curve_distance}
        next_curve_dir: {self.next_curve_direction}
        """

class SimState1(SimState):
    def __init__(self) -> None:
        super().__init__()

    def get_info_from_center_line(self, pos, rot):
        arg = get_info_from_center_line_1(pos, rot)
        self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction = arg

    def normalize(self):
        self.linear_speed, self.angular_speed, self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction = normalize_info(self)

    def get_state(self):
        return [self.linear_speed, self.angular_speed, self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction]
    
    def __str__(self):
        return f"""
        SimState1
        lin_speed: {self.linear_speed}
        ang_speed: {self.angular_speed}
        dist_to_center: {self.distance_to_centerline}
        angle_to_centerline: {self.angle_to_centerline}
        next_curve_dist: {self.next_curve_distance}
        next_curve_dir: {self.next_curve_direction}
        """
