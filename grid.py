#!/usr/bin/env python
import argparse
import math
import re
import sys

import numpy as np
import numpy.linalg as la
from scipy import interpolate

BASE_GRID = 300.0
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


class ParseError(Exception):
    pass

class GridError(Exception):
    pass


class GridRef(object):

    def __init__(self, letter, major, keypads=None):
        self.letter = letter.upper()
        self.major = int(major)

        if keypads:
            self.keypads = keypads
            self._verify_keypads()
        else:
            self.keypads = []

        self._vector = None

    def __str__(self):
        return "{}{}K{}".format(self.letter, self.major, self.keypads)

    def __repr__(self):
        return "<GridRef: {}>".format(self)

    def _verify_keypads(self):
        for k in self.keypads:
            if k < 1 or k > 9:
                raise GridError("Keypads must be in the range 1-9")

    @property
    def vector(self):
        if not self._vector:
            self._calculate()

        return self._vector

    def _kp_to_pos(self, kp):
        x = (kp - 1) % 3 - 1
        y = 1 - (kp - 1) / 3
        return np.array([x, y], dtype='float64')

    def _letter_num(self):
        num = ord(self.letter) - 64
        assert(num >= 1 and num <= 26)
        return num

    def _calculate(self):
        base_x = self._letter_num() - 0.5
        base_y = self.major - 0.5
        basecoord = np.array([base_x, base_y]) * BASE_GRID

        for n, kp in enumerate(self.keypads):
            subcoord = self._kp_to_pos(kp)
            subcoord *= BASE_GRID / (3**(n + 1))
            basecoord = basecoord + subcoord

        self._vector = basecoord

    @classmethod
    def from_string(cls, gridstr):
        m = re.match(r'^(\w)(\d{1,2})(?:K(\d+))?$', gridstr)
        if m:
            letter = str(m.group(1))
            major = int(m.group(2))
            if m.group(3):
                keypads = [int(x) for x in m.group(3) if x > 0]
            else:
                keypads = None
            return cls(letter, major, keypads)
        raise ParseError("Bad grid string")


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
    # parser.add_argument('target')
    args = parser.parse_args()

    print GridRef.from_string(args.base).vector
    sys.exit(0)

    base = grid_to_pos(args.base)
    target = grid_to_pos(args.target)

    calculate(base, target)
