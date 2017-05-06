import numpy as np
import re

from .errors import GridError, ParseError

BASE_GRID = 300.0


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
