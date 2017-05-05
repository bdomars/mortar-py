#!/usr/bin/env python
import argparse
import math

import numpy as np
import numpy.linalg as la
from scipy import interpolate

base_grid = 300.0
north_vec = np.array([0, -100])

ranges = np.arange(50, 1251, 50)
mils = np.array([
    1579,
    1558,
    1538,
    1517,
    1496,
    1475,
    1453,
    1431,
    1409,
    1387,
    1364,
    1341,
    1317,
    1292,
    1267,
    1240,
    1212,
    1183,
    1152,
    1118,
    1081,
    1039,
    988,
    918,
    800
])

interp_mils = interpolate.interp1d(ranges, mils)
mils_spline = interpolate.splrep(ranges, mils)


def kp_to_pos(kp):
    x = (kp - 1) % 3 - 1
    y = 1 - (kp - 1) / 3
    return np.array([x, y])


def gridletter(chr):
    assert(len(chr) == 1)
    num = ord(chr.upper()) - 65
    assert(num >= 0 and num < 26)
    return num + 1


def grid_to_pos(gridstr):
    base_x = gridletter(gridstr[0]) + 0.5
    base_y = int(gridstr[1]) - 1 + 0.5
    basecoord = np.array([base_x, base_y]) * base_grid
    kps = gridstr[2:]
    for n, kp in enumerate(kps):
        subcoord = kp_to_pos(int(kp)) * (base_grid / (3**(n + 1)))
        basecoord = basecoord + subcoord

    return basecoord


def get_angle(to_target):
    dot = np.dot(north_vec, to_target)
    cross = np.cross(north_vec, to_target)
    angle = math.degrees(np.arctan2(cross, dot))

    if angle < 0:
        return 180 + (180 - abs(angle))
    else:
        return angle


def get_elevation_lerp(dist):
    return float(interp_mils(dist))


def get_elevation_spline(dist):
    reachable = dist >= 50 and dist <= 1250
    return reachable, float(interpolate.splev(dist, mils_spline))


def get_range(to_target):
    return la.norm(to_target)


def calculate(base, target):
    to_target = target - base

    angle = get_angle(to_target)
    distance = get_range(to_target)
    reachable, elev = get_elevation_spline(distance)

    print
    print "Targeting solution"
    print "-------------------------------"
    print "Angle      : {:>10.1f} degrees".format(angle)
    print "Distance   : {:>10.1f} meters".format(distance)
    if reachable:
        print "Elevation  : {:>10.1f} mils".format(elev)
    else:
        print "Elevation  :        N/A"
    print
    print "Ready to fire!"
    print


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('base')
    parser.add_argument('target')
    args = parser.parse_args()

    base = grid_to_pos(args.base)
    target = grid_to_pos(args.target)

    calculate(base, target)



