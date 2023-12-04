from tminterface.client import Client
from tminterface.interface import TMInterface
from time import sleep
from utils import get_info_from_center_line, normalize_info

"""
speed
acceleration
turning_rate
lateral_velocity
distance_to_centerline
angle_to_centerline
next_curve_distance
next_curve_direction
"""

class SimState():
    def __init__(self) -> None:
        #                     Maxes
        self.linear_speed = 0 # 240 (about 840 in TM) (about 70 actual in the first map)
        self.angular_speed = 0 # Got to 30 max on grass, might want to drop or change
        self.distance_to_centerline = 0 # 14
        self.angle_to_centerline = 0 # pi
        self.next_curve_distance = 0 # pi on curves and about 0.5 on straight
        self.next_curve_direction = 0 # -1 and 1, 0 on road to fin

    def get_info_from_center_line(self, arg):
        self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction = arg

    def normalize(self):
        self.linear_speed, self.angular_speed, self.distance_to_centerline, self.angle_to_centerline, self.next_curve_distance, self.next_curve_direction = normalize_info(self)

    def __str__(self):
        return f"""
        lin_speed: {self.linear_speed}
        ang_speed: {self.angular_speed}
        dist_to_center: {self.distance_to_centerline}
        angle_to_centerline: {self.angle_to_centerline}
        next_curve_dist: {self.next_curve_distance}
        next_curve_dir: {self.next_curve_direction}
        """

class SimStateClient(Client):
    """
    Client for a TMInterface instance.
    Its only job is to get the simulation state that is used by the gym env for reward computation.
    """

    def __init__(self):
        super().__init__()
        self.sim_state = None

    def on_run_step(self, iface, _time: int):
        self.sim_state = iface.get_simulation_state()

class SimStateInterface():
    def __init__(self):
        self.client = SimStateClient()
        self.interface = TMInterface()
        
        self.interface.register(self.client)

        self.state = SimState()

    def step(self):
        pos = self.client.sim_state.dyna.current_state.position
        rot = self.client.sim_state.dyna.current_state.rotation 
        linear_speed = self.client.sim_state.dyna.current_state.linear_speed

        self.state.get_info_from_center_line(get_info_from_center_line(pos, rot))
        self.state.linear_speed = linear_speed[0] * rot[0, 2] + linear_speed[2] * rot[0, 0]
        self.state.angular_speed = - linear_speed[0] * rot[0, 0] + linear_speed[2] * rot[0, 2]

        self.state.normalize()

if __name__ == '__main__':
    interface = SimStateInterface()

    while True:
        sleep(0.5)

        # rot = interface.client.sim_state.dyna.current_state.rotation 
        # linear_speed = interface.client.sim_state.dyna.current_state.linear_speed
        # print(- linear_speed[0] * rot[0, 0] + linear_speed[2] * rot[0, 2])

        interface.step()

        print(interface.state)




"""

USEFULL INFO:

{'dyna': {'current_state': {
        'rotation': 
            [[-4.637241727323271e-05 -1.608470847713761e-05 1.0000001192092896] --> 0; 1
            [-1.1713937055901624e-05 1.0 1.6084166418295354e-05]
            [-1.0000001192092896 -1.1713193998730276e-05 -4.6372413635253906e-05]],
        'position': [491.1990661621094 25.314067840576172 111.99974822998047], 
        'linear_speed': [-4.065921530127525e-06 7.042125798761845e-05 -0.008362118154764175],
        'angular_speed': [-0.0006353310309350491 -9.349186314011604e-09 0.00013702776050195098],
        'force': [-0.00012449565110728145 -6.198811024660245e-05 -1.6709308624267578], 
        'torque': [-0.14622393250465393 -2.1979212760925293e-06 -0.006425691768527031]}}, 
        'scene_mobil': {'sync_vehicle_state': {'speed_forward': 0.0, 'speed_sideward': 0.0}, 'is_sliding': False}}

"""

"""
FULL AVAILABLE INFO:

[SimStateData object at 0x1ebaa362a10]
version (int): 1
context_mode (int): 1
flags (int): 159
timers (ndarray):
        [185040 185030 0 185040 185030 0 185040 185030 0 185200 185100 0 185040
         185030 0 185040]   (37 more items...)
dyna (HmsDynaStruct):
        previous_state (HmsDynaStateStruct):
                quat (ndarray):
                        [0.6457754373550415 -0.00013948054402135313 -0.7635274529457092
                         -0.0001362227339996025]
                rotation (ndarray):
                        [[-0.16594842076301575 0.0003889330546371639 -0.9861344695091248]
                         [3.7055855500511825e-05 0.9999998807907104 0.00038816581945866346]
                         [0.9861345887184143 2.7873378712683916e-05 -0.16594845056533813]]
                position (ndarray): [445.9747619628906 88.0136489868164 698.1837158203125]
                linear_speed (ndarray): [1.4753810167312622 0.0014956863597035408 0.24804866313934326]
                add_linear_speed (ndarray): [0.0 0.0 0.0]
                angular_speed (ndarray): [0.04548431932926178 0.00011037500371458009 0.008167100138962269]
                force (ndarray): [-1.4242181777954102 0.0572199821472168 -0.22207790613174438]
                torque (ndarray): [-0.07923659682273865 -0.001937411492690444 -0.017784422263503075]
                inverse_inertia_tensor (ndarray):
                        [[1.1801722049713135 -0.0002756043104454875 0.11782620847225189]
                         [-0.0002756043104454875 0.4800000786781311 -4.637921301764436e-05]
                         [0.11782620847225189 -4.637921301764436e-05 0.49982815980911255]]
                unknown (float): 0.0
                not_tweaked_linear_speed (ndarray): [0.0 0.0 0.0]
                owner (int): 610682032
        current_state (HmsDynaStateStruct):
                quat (ndarray):
                        [0.6457758545875549 3.856169860227965e-05 -0.763526976108551
                         -0.0002834947081282735]
                rotation (ndarray):
                        [[-0.16594700515270233 0.00030726229306310415 -0.9861345887184143]
                         [-0.00042503385338932276 0.9999998211860657 0.0003831072826869786]
                         [0.9861345887184143 0.0004827161319553852 -0.1659468412399292]]
                position (ndarray): [445.9895324707031 88.01366424560547 698.18603515625]
                linear_speed (ndarray): [1.4611799716949463 0.002014692174270749 0.245834618806839]
                add_linear_speed (ndarray): [0.0 0.0 0.0]
                angular_speed (ndarray): [0.043879713863134384 0.0001022124124574475 0.007889803498983383]
                force (ndarray): [-1.4201092720031738 0.051900386810302734 -0.22140413522720337]
                torque (ndarray): [-0.13356885313987732 -0.0017795497551560402 -0.023991849273443222]
                inverse_inertia_tensor (ndarray):
                        [[1.1801722049713135 -0.0002720126649364829 0.11782505363225937]
                         [-0.0002720126649364829 0.4800001084804535 -4.5774308091495186e-05]
                         [0.11782505363225937 -4.577429353957996e-05 0.49982765316963196]]
                unknown (float): 0.0
                not_tweaked_linear_speed (ndarray): [0.0 0.0 0.0]
                owner (int): 610682032
        temp_state (HmsDynaStateStruct):
                quat (ndarray):
                        [0.6457754373550415 -0.00013948054402135313 -0.7635274529457092
                         -0.0001362227339996025]
                rotation (ndarray):
                        [[-0.16594842076301575 0.0003889330546371639 -0.9861344695091248]
                         [3.7055855500511825e-05 0.9999998807907104 0.00038816581945866346]
                         [0.9861345887184143 2.7873378712683916e-05 -0.16594845056533813]]
                position (ndarray): [445.9747619628906 88.0136489868164 698.1837158203125]
                linear_speed (ndarray): [1.4753810167312622 0.0014956863597035408 0.24804866313934326]
                add_linear_speed (ndarray): [0.0 0.0 0.0]
                angular_speed (ndarray): [0.04548431932926178 0.00011037500371458009 0.008167100138962269]
                force (ndarray): [-1.4242181777954102 0.0572199821472168 -0.22207790613174438]
                torque (ndarray): [-0.07923659682273865 -0.001937411492690444 -0.017784422263503075]
                inverse_inertia_tensor (ndarray):
                        [[1.1801722049713135 -0.0002756043104454875 0.11782620847225189]
                         [-0.0002756043104454875 0.4800000786781311 -4.637921301764436e-05]
                         [0.11782620847225189 -4.637921301764436e-05 0.49982815980911255]]
                unknown (float): 0.0
                not_tweaked_linear_speed (ndarray): [0.0 0.0 0.0]
                owner (int): 610682032
        rest (bytearray): [ BC 45 66 24 70 46 66 24 04 00 00 00 18 FD B5 17  (600 more bytes...) ]
scene_mobil (SceneVehicleCar):
        is_update_async (bool): True
        input_gas (float): 0.0
        input_brake (float): 0.0
        input_steer (float): 0.0
        is_light_trials_set (bool): False
        horn_limit (int): 3
        quality (int): 2
        max_linear_speed (float): 277.77777099609375
        gearbox_state (int): 1
        block_flags (int): 4
        prev_sync_vehicle_state (SceneVehicleCarState):
                speed_forward (float): 7.914471980247305e-27
                speed_sideward (float): 5.605193857299268e-45
                input_steer (float): 8.305134512699733e-25
                input_gas (float): -1.496086835861206
                input_brake (float): -0.00022771954536437988
                is_turbo (bool): False
                rpm (float): 0.2480505406856537
                gearbox_state (int): 0
                rest (bytearray): [ 00 C0 A8 45 01 00 00 00 01 00 00 00 01 00 00 00  (12 more bytes...) ]
        sync_vehicle_state (SceneVehicleCarState):
                speed_forward (float): 0.0
                speed_sideward (float): 0.0
                input_steer (float): 0.0
                input_gas (float): -1.4817148447036743
                input_brake (float): -5.327165126800537e-05
                is_turbo (bool): False
                rpm (float): 0.24583716690540314
                gearbox_state (int): 0
                rest (bytearray): [ 00 80 A7 45 01 00 00 00 01 00 00 00 01 00 00 00  (12 more bytes...) ]
        async_vehicle_state (SceneVehicleCarState):
                speed_forward (float): 0.0
                speed_sideward (float): 0.0
                input_steer (float): 0.0
                input_gas (float): -1.519173264503479
                input_brake (float): -0.0005062341806478798
                is_turbo (bool): False
                rpm (float): 0.25161388516426086
                gearbox_state (int): 0
                rest (bytearray): [ 00 C0 AA 45 01 00 00 00 01 00 00 00 01 00 00 00  (12 more bytes...) ]
        prev_async_vehicle_state (SceneVehicleCarState):
                speed_forward (float): 0.0
                speed_sideward (float): 0.0
                input_steer (float): 0.0
                input_gas (float): -1.5583680868148804
                input_brake (float): -0.0009493827819824219
                is_turbo (bool): False
                rpm (float): 0.2576931118965149
                gearbox_state (int): 0
                rest (bytearray): [ 00 20 AE 45 01 00 00 00 01 00 00 00 01 00 00 00  (12 more bytes...) ]
        engine (Engine):
                max_rpm (float): 11000.0
                braking_factor (float): -0.0
                clamped_rpm (float): 5360.0
                actual_rpm (float): 558.885009765625
                slide_factor (float): 1.0
                rear_gear (int): 0
                gear (int): 1
        has_any_lateral_contact (bool): False
        last_has_any_lateral_contact_time (int): -1
        water_forces_applied (bool): False
        turning_rate (float): 0.0
        turbo_boost_factor (float): 0.0
        last_turbo_type_change_time (int): 0
        last_turbo_time (int): 0
        turbo_type (int): 0
        roulette_value (float): 0.0
        is_freewheeling (bool): False
        is_sliding (bool): False
        wheel_contact_absorb_counter (int): 0
        burnout_state (int): 0
        current_local_speed (ndarray): [-0.00022771954536437988 0.0020764244254678488 -1.496086835861206]
        total_central_force_added (ndarray): [0.018444247543811798 30.051342010498047 1.4488251209259033]
        is_rubber_ball (bool): False
        saved_state (ndarray):
                [[0.0 0.0 0.0]
                 [0.0 0.0 0.0]
                 [0.0 0.0 0.0]
                 [0.0 0.0 0.0]]
simulation_wheels (ndarray):
        [[SimulationWheel object at 0x1ebaa362e00]
         steerable (bool): True
         field_8 (int): 1052401205
         surface_handler (SurfaceHandler):
                unknown (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]
                         [0.8630120158195496 0.35249999165534973 1.7820889949798584]]
                rotation (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                position (ndarray): [0.8630120158195496 0.33976924419403076 1.7820889949798584]
         field_112 (ndarray):
                [[1.0 0.0 0.0]
                 [0.0 1.0 0.0]
                 [0.0 0.0 1.0]
                 [0.0 0.0 0.0]]
         field_160 (int): 1065353216
         field_164 (int): 1065353216
         offset_from_vehicle (ndarray): [0.8630120158195496 0.35249999165534973 1.7820889949798584]
         real_time_state (RealTimeState):
                damper_absorb (float): 0.012730746529996395
                field_4 (float): -0.03841891512274742
                field_8 (float): 0.01024881936609745
                field_12 (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                field_48 (ndarray):
                        [[1.0 3.707134601427242e-05 8.881784197001252e-16]
                         [-3.7071342376293615e-05 0.9999999403953552 -0.00038816247251816094]
                         [-1.4389705427220179e-08 0.00038816247251816094 0.9999999403953552]]
                field_84 (ndarray): [0.8630386590957642 -0.013980099931359291 1.7819358110427856]
                field_108 (float): -4.110128879547119
                has_ground_contact (bool): True
                contact_material_id (int): 1043988496
                is_sliding (bool): False
                relative_rotz_axis (ndarray): [-0.16594842076301575 0.0003889330546371639 -0.9861344695091248]
                nb_ground_contacts (int): 1
                field_144 (ndarray): [-0.00042505437158979475 0.9999997615814209 0.0003831157519016415]
                rest (bytearray): [ 67 98 97 44 00 00 00 80 00 00 00 80 ]
         field_348 (int): 0
         contact_relative_local_distance (ndarray): [0.0 0.0 0.0]
         prev_sync_wheel_state (WheelState):
                rest (bytearray): [ 07 E0 56 3C B8 99 97 44 00 00 00 80 10 00 03 3E  (84 more bytes...) ]
         sync_wheel_state (WheelState):
                rest (bytearray): [ 9F 94 50 3C 67 98 97 44 00 00 00 80 10 00 03 3E  (84 more bytes...) ]
         field_564 (WheelState):
                rest (bytearray): [ 5B 4F 72 3C 85 9F 97 44 00 00 00 80 10 00 10 3E  (84 more bytes...) ]
         async_wheel_state (WheelState):
                rest (bytearray): [ C4 4C 61 3C DA 9B 97 44 00 00 00 80 10 00 10 3E  (84 more bytes...) ]
         [SimulationWheel object at 0x1ebaa363130]
         steerable (bool): True
         field_8 (int): 1052401205
         surface_handler (SurfaceHandler):
                unknown (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]
                         [-0.8629900217056274 0.35249999165534973 1.7820889949798584]]
                rotation (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                position (ndarray): [-0.8629900217056274 0.33983102440834045 1.7820889949798584]
         field_112 (ndarray):
                [[1.0 0.0 0.0]
                 [0.0 1.0 0.0]
                 [0.0 0.0 1.0]
                 [0.0 0.0 0.0]]
         field_160 (int): 1065353216
         field_164 (int): 1065353216
         offset_from_vehicle (ndarray): [-0.8629900217056274 0.35249999165534973 1.7820889949798584]
         real_time_state (RealTimeState):
                damper_absorb (float): 0.0126689737662673
                field_4 (float): 0.03895973414182663
                field_8 (float): 0.009455435909330845
                field_12 (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                field_48 (ndarray):
                        [[1.0 3.707134601427242e-05 8.881784197001252e-16]
                         [-3.7071342376293615e-05 0.9999999403953552 -0.00038816247251816094]
                         [-1.4389705427220179e-08 0.00038816247251816094 0.9999999403953552]]
                field_84 (ndarray): [-0.8629770278930664 -0.01471372228115797 1.7819554805755615]
                field_108 (float): -4.110128879547119
                has_ground_contact (bool): True
                contact_material_id (int): 1040515088
                is_sliding (bool): False
                relative_rotz_axis (ndarray): [-0.16594842076301575 0.0003889330546371639 -0.9861344695091248]
                nb_ground_contacts (int): 1
                field_144 (ndarray): [-0.00042505437158979475 0.9999997615814209 0.0003831157519016415]
                rest (bytearray): [ EC 9B 97 44 00 00 00 80 00 00 00 80 ]
         field_348 (int): 0
         contact_relative_local_distance (ndarray): [0.0 0.0 0.0]
         prev_sync_wheel_state (WheelState):
                rest (bytearray): [ 70 2F 49 3C 3D 9D 97 44 00 00 00 80 10 00 32 3E  (84 more bytes...) ]
         sync_wheel_state (WheelState):
                rest (bytearray): [ 87 91 4F 3C EC 9B 97 44 00 00 00 80 10 00 32 3E  (84 more bytes...) ]
         field_564 (WheelState):
                rest (bytearray): [ 02 02 30 3C 0A A3 97 44 00 00 00 80 10 00 3A 3E  (84 more bytes...) ]
         async_wheel_state (WheelState):
                rest (bytearray): [ 7A 43 3F 3C 5F 9F 97 44 00 00 00 80 10 00 3A 3E  (84 more bytes...) ]
         [SimulationWheel object at 0x1ebaa362dd0]
         steerable (bool): False
         field_8 (int): 1052401205
         surface_handler (SurfaceHandler):
                unknown (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]
                         [-0.8849999904632568 0.3525039851665497 -1.2055020332336426]]
                rotation (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                position (ndarray): [-0.8849999904632568 0.3409348428249359 -1.2055020332336426]
         field_112 (ndarray):
                [[1.0 0.0 0.0]
                 [0.0 1.0 0.0]
                 [0.0 0.0 1.0]
                 [0.0 0.0 0.0]]
         field_160 (int): 1065353216
         field_164 (int): 1065353216
         offset_from_vehicle (ndarray): [-0.8849999904632568 0.3525039851665497 -1.2055020332336426]
         real_time_state (RealTimeState):
                damper_absorb (float): 0.011569135822355747
                field_4 (float): 0.040962543338537216
                field_8 (float): 0.009486114606261253
                field_12 (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                field_48 (ndarray):
                        [[1.0 3.707134601427242e-05 8.881784197001252e-16]
                         [-3.7071342376293615e-05 0.9999999403953552 -0.00038816247251816094]
                         [-1.4389705427220179e-08 0.00038816247251816094 0.9999999403953552]]
                field_84 (ndarray): [-0.8849451541900635 -0.013578484766185284 -1.205651879310608]
                field_108 (float): -4.110128879547119
                has_ground_contact (bool): True
                contact_material_id (int): 1044185104
                is_sliding (bool): False
                relative_rotz_axis (ndarray): [-0.16594842076301575 0.0003889330546371639 -0.9861344695091248]
                nb_ground_contacts (int): 1
                field_144 (ndarray): [-0.00042505437158979475 0.9999997615814209 0.0003831157519016415]
                rest (bytearray): [ EE 9A 97 44 00 00 00 00 00 00 00 00 ]
         field_348 (int): 0
         contact_relative_local_distance (ndarray): [0.0 0.0 0.0]
         prev_sync_wheel_state (WheelState):
                rest (bytearray): [ 61 D6 36 3C 3F 9C 97 44 00 00 00 00 10 00 03 3E  (84 more bytes...) ]
         sync_wheel_state (WheelState):
                rest (bytearray): [ 79 8C 3D 3C EE 9A 97 44 00 00 00 00 10 00 03 3E  (84 more bytes...) ]
         field_564 (WheelState):
                rest (bytearray): [ 0B D7 23 3C 0C A2 97 44 00 00 00 00 10 00 14 3E  (84 more bytes...) ]
         async_wheel_state (WheelState):
                rest (bytearray): [ 92 39 2C 3C 61 9E 97 44 00 00 00 00 10 00 14 3E  (84 more bytes...) ]
         [SimulationWheel object at 0x1ebaa363700]
         steerable (bool): False
         field_8 (int): 1052401205
         surface_handler (SurfaceHandler):
                unknown (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]
                         [0.8850020170211792 0.3525039851665497 -1.2055020332336426]]
                rotation (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                position (ndarray): [0.8850020170211792 0.3408758044242859 -1.2055020332336426]
         field_112 (ndarray):
                [[1.0 0.0 0.0]
                 [0.0 1.0 0.0]
                 [0.0 0.0 1.0]
                 [0.0 0.0 0.0]]
         field_160 (int): 1065353216
         field_164 (int): 1065353216
         offset_from_vehicle (ndarray): [0.8850020170211792 0.3525039851665497 -1.2055020332336426]
         real_time_state (RealTimeState):
                damper_absorb (float): 0.011628177016973495
                field_4 (float): -0.0387364961206913
                field_8 (float): 0.010301628150045872
                field_12 (ndarray):
                        [[1.0 0.0 0.0]
                         [0.0 1.0 0.0]
                         [0.0 0.0 1.0]]
                field_48 (ndarray):
                        [[1.0 3.707134601427242e-05 8.881784197001252e-16]
                         [-3.7071342376293615e-05 0.9999999403953552 -0.00038816247251816094]
                         [-1.4389705427220179e-08 0.00038816247251816094 0.9999999403953552]]
                field_84 (ndarray): [0.8850200772285461 -0.012826194055378437 -1.205640196800232]
                field_108 (float): -4.110128879547119
                has_ground_contact (bool): True
                contact_material_id (int): 1040449552
                is_sliding (bool): False
                relative_rotz_axis (ndarray): [-0.16594842076301575 0.0003889330546371639 -0.9861344695091248]
                nb_ground_contacts (int): 1
                field_144 (ndarray): [-0.00042505437158979475 0.9999997615814209 0.0003831157519016415]
                rest (bytearray): [ D1 96 97 44 00 00 00 00 00 00 00 00 ]
         field_348 (int): 0
         contact_relative_local_distance (ndarray): [0.0 0.0 0.0]
         prev_sync_wheel_state (WheelState):
                rest (bytearray): [ D6 DC 44 3C 22 98 97 44 00 00 00 00 10 00 31 3E  (84 more bytes...) ]
         sync_wheel_state (WheelState):
                rest (bytearray): [ 1C 84 3E 3C D1 96 97 44 00 00 00 00 10 00 31 3E  (84 more bytes...) ]
         field_564 (WheelState):
                rest (bytearray): [ 94 4E 60 3C EF 9D 97 44 00 00 00 00 10 00 3A 3E  (84 more bytes...) ]
         async_wheel_state (WheelState):
                rest (bytearray): [ B2 1E 4F 3C 44 9A 97 44 00 00 00 00 10 00 3A 3E  (84 more bytes...) ]     ]
plug_solid (bytearray): [ 00 00 80 3F 90 C2 F5 3E 00 00 00 00 00 00 00 00  (52 more bytes...) ]
cmd_buffer_core (bytearray): [ 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  (248 more bytes...) ]
player_info (PlayerInfoStruct):
        team (int): 0
        prev_race_time (int): -1
        race_start_time (int): 2600
        race_time (int): 182420
        race_best_time (int): 24530
        lap_start_time (int): 2600
        lap_time (int): 182420
        lap_best_time (int): -1
        min_respawns (int): 0
        nb_completed (int): 0
        max_completed (int): 0
        stunts_score (int): 0
        best_stunts_score (int): 0
        cur_checkpoint (int): 0
        average_rank (float): 0.0
        current_race_rank (int): 32
        current_round_rank (int): 0
        current_time (int): 0
        race_state (int): 1
        ready_enum (int): 0
        round_num (int): 0
        offset_current_cp (float): 0.0
        cur_lap_cp_count (int): 0
        cur_cp_count (int): 0
        cur_lap (int): 0
        race_finished (bool): False
        display_speed (int): 5
        finish_not_passed (bool): True
        countdown_time (int): 2600
        rest (bytearray): [ 94 C8 02 00 00 FF 00 00 00 00 00 00 78 C8 B2 00  (16 more bytes...) ]
internal_input_state (ndarray):
        [[CachedInput object at 0x1ebaa363850]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa362890]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa363670]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa362ef0]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa362d40]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa362a40]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa3632b0]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa362ec0]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa362b90]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0
         [CachedInput object at 0x1ebaa363310]
         time (int): 0
         event (Event):
                time (int): 0
                input_data (int): 0                 ]
input_running_event (Event):
        time (int): 100000
        input_data (int): 150994945
input_finish_event (Event):
        time (int): 0
        input_data (int): 0
input_accelerate_event (Event):
        time (int): 280990
        input_data (int): 67108864
input_brake_event (Event):
        time (int): 281020
        input_data (int): 50331648
input_left_event (Event):
        time (int): 281030
        input_data (int): 0
input_right_event (Event):
        time (int): 275860
        input_data (int): 16777216
input_steer_event (Event):
        time (int): 0
        input_data (int): 0
input_gas_event (Event):
        time (int): 0
        input_data (int): 0
num_respawns (int): 0
cp_data (CheckpointData):
        reserved (int): 0
        cp_states_length (int): 3
        cp_states (ndarray): [False False False]
        cp_times_length (int): 3
        cp_times (ndarray):
                [[CheckpointTime object at 0x1ebaa362ef0]
                 time (int): -1
                 stunts_score (int): 0
                 [CheckpointTime object at 0x1ebaa362bc0]
                 time (int): -1
                 stunts_score (int): 0
                 [CheckpointTime object at 0x1ebaa362f20]
                 time (int): -1
                 stunts_score (int): 0        
"""