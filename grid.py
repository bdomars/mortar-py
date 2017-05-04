#!/usr/bin/env python
import argparse
import math

import numpy as np
import numpy.linalg as la


base_grid = 300.0
north_vec = np.array([0, -100])


def kp_to_pos(kp):
    x = (kp - 1) % 3
    y = 2 - ((kp - 1) / 3)
    return np.array([x, y])


def gridletter(chr):
    assert(len(chr) == 1)
    num = ord(chr.upper()) - 65
    assert(num >= 0 and num < 26)
    return num


def grid_to_pos(gridstr):
    base_x = gridletter(gridstr[0])
    base_y = int(gridstr[1]) - 1
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


def get_range(to_target):
    return la.norm(to_target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('base')
    parser.add_argument('target')
    args = parser.parse_args()

    base = grid_to_pos(args.base)
    target = grid_to_pos(args.target)

    to_target = target - base

    angle = get_angle(to_target)
    range = get_range(to_target)

    print "Angle = {}".format(angle)
    print "Range = {}m".format(range)
