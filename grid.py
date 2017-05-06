#!/usr/bin/env python
import argparse
import math

import numpy as np
import numpy.linalg as la
from scipy import interpolate

from mortarlib import GridRef

NORTH = np.array([0, -100])

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


def get_angle(to_target):
    dot = np.dot(NORTH, to_target)
    cross = np.cross(NORTH, to_target)
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

    base = GridRef.from_string(args.base)
    target = GridRef.from_string(args.target)

    calculate(base.vector, target.vector)
