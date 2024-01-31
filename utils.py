from math import atan2, sqrt, pi

from constants import LEVEL

START_0 = 459.2
END_0 = 809.6
CENTER_0 = 368

CURVES_1 = [
    [272, 0, 544],
    [366, 0, 544],
    [464, 0, 544],
    [560, 0, 544],
    [656, 0, 544],
    [752, 0, 544],
]

def get_info_from_center_line_0(car_pos, car_rot):
    return CENTER_0 - car_pos[0], atan2(car_rot[0, 2], car_rot[0, 0]), END_0 - car_pos[2], 0


def get_info_from_center_line_by2curves(car_pos, car_rot, curve_pos1, curve_pos2, is_upper_curve: bool):
    r =  abs(curve_pos2[0] - curve_pos1[0]) / 2
    center_pos = (curve_pos1[0] + curve_pos2[0]) / 2, curve_pos1[1], curve_pos1[2]
    angle = atan2(car_pos[2] - center_pos[2], car_pos[0] - center_pos[0])
    x = car_pos[0] - center_pos[0]
    y = car_pos[2] - center_pos[2]
    h = sqrt(x**2 + y**2)
    distance = r - h
    ret_angle = angle + (pi/2 if is_upper_curve else -pi/2) - atan2(car_rot[0, 0], car_rot[0, 2])
    if (ret_angle > pi):
        ret_angle -= 2*pi
    return (distance * (-1 if is_upper_curve else 1),
            ret_angle,
            abs(angle),
            -1 if is_upper_curve else 1)

def get_info_from_center_line_1(car_pos, car_rot):
    c1, c2 = 0, 0
        
    curves = list(map(lambda el: None if el[0] == len(CURVES_1) - 1 else [el[1], CURVES_1[el[0] + 1]], enumerate(CURVES_1)))
    i = ii = 0
    for c in curves:
        if c == None:
            break
        if (car_pos[0] >= c[0][0] - 16 and car_pos[0] <= c[1][0] + 16):
            if car_pos[2] >= 544 and i % 2 == 0 or car_pos[2] <= 544 and i % 2 == 1:
                c1, c2 = c
                ii = i
        i += 1

    if (c1 == 0):
        if car_pos[0] < 544:
            return car_pos[0] - 272, atan2(car_rot[0, 0], car_rot[0, 2]) - pi/2, (544 - car_pos[2]) / 20, -1
        elif car_pos[0] > 544:
            return 752 - car_pos[0], atan2(car_rot[0, 0], car_rot[0, 2]) - pi/2, (car_pos[2] - 534) / 20, 0

    return get_info_from_center_line_by2curves(car_pos, car_rot, c1, c2, ii % 2 == 1)

def normalize_info(info):
    result = info
    result.linear_speed = info.linear_speed / (300 if LEVEL == 0 else 70)
    result.angular_speed = info.angular_speed / 30
    result.distance_to_centerline = info.distance_to_centerline / 14
    result.angle_to_centerline = info.angle_to_centerline / pi
    result.next_curve_distance = info.next_curve_distance / ((END_0 - START_0 + 65) if LEVEL == 0 else pi)
    result.next_curve_direction = info.next_curve_direction
    return (result.linear_speed, result.angular_speed, result.distance_to_centerline, result.angle_to_centerline, result.next_curve_distance, result.next_curve_direction)

if __name__ == '__main__':
    print('wrong file dumbass')

# [283.6285400390625 41.373592376708984 533.5134887695312]

"""
Coords

Z:
15: 496 - upper curve
17: 592 - lower curve

X:
272 - start (8)
320 - 1st curve
368 - 1st-2nd curves transition
416 - 2nd curve
464 - 2nd-3rd curves transition
512 - 3rd curve
560 - 3rd-4th curves transition
608 - 4th curve
656 - 4th-5th curves transition
704 - 5th curve
752 - finish (23)
"""

"""
Quats:

start:
[[1.0 2.7062228582508396e-06 1.4599955875382875e-06] --> 1; 0
 [-2.7062237677455414e-06 1.0 5.685234327756916e-07]
 [-1.4599939959225594e-06 -5.685274118150119e-07 1.0]]

right:
[[-2.0294960449973587e-06 -3.233347160858102e-05 -0.9999999403953552] --> 0; -1
 [-0.0001407439704053104 1.0 -3.233318784623407e-05]
 [0.9999999403953552 0.00014074389764573425 -2.0265579223632812e-06]] 

left:
[[-4.7792468649277e-07 -9.896371921058744e-05 1.0] --> 0; 1
 [-3.300890602986328e-05 1.0 9.896370465867221e-05]
 [-1.0 -3.30088623741176e-05 -4.76837158203125e-07]]

back:
[[-1.0 0.00013821393076796085 1.4387745750354952e-06] --> -1; 0
 [0.00013821393076796085 1.0 -6.6381685428495985e-06]
 [-1.4396920278159087e-06 -6.63796936350991e-06 -1.0]]

"""