from math import atan2, sqrt, pi

CURVES = [
    [272, 0, 544],
    [366, 0, 544],
    [464, 0, 544],
    [560, 0, 544],
    [656, 0, 544],
    [752, 0, 544],
]

def get_info_from_center_line_by2curves(car_pos, curve_pos1, curve_pos2):
    r =  abs(curve_pos2[0] - curve_pos1[0]) / 2
    center_pos = (curve_pos1[0] + curve_pos2[0]) / 2, curve_pos1[1], curve_pos1[2]
    angle = atan2(car_pos[2] - center_pos[2], car_pos[0] - center_pos[0])
    x = car_pos[0] - center_pos[0]
    y = car_pos[2] - center_pos[2]
    h = sqrt(x**2 + y**2)
    distance = r - h
    return distance, angle * 180 / pi

def get_info_from_center_line(car_pos):
    c1, c2 = 0, 0
        
    curves = list(map(lambda el: None if el[0] == len(CURVES) - 1 else [el[1], CURVES[el[0] + 1]], enumerate(CURVES)))
    i = 0
    for c in curves:
        if c == None:
            break
        if (car_pos[0] >= c[0][0] - 16 and car_pos[0] <= c[1][0] + 16):
            if car_pos[2] >= 544 and i % 2 == 0 or car_pos[2] <= 544 and i % 2 == 1:
                c1, c2 = c
        i += 1

    return get_info_from_center_line_by2curves(car_pos, c1, c2)

if __name__ == '__main__':
    print(get_info_from_center_line(
        [377.5801086425781, 41.35907745361328, 530.1361083984375]
    ))
