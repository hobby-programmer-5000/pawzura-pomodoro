"""Continuous seated/standing transitions, independent of the countdown clock."""
from time import monotonic


class Posture:
    SIT_SECONDS = .65
    STAND_SECONDS = .75

    def __init__(self, clock=None):
        self.clock = clock or monotonic
        self.phase = "ready"
        self.amount = 0.0
        self.target = 0.0
        self.origin = 0.0
        self.started = self.clock()
        self.duration = 0.0

    def update(self):
        elapsed = max(0.0, self.clock() - self.started)
        progress = min(1.0, elapsed / self.duration) if self.duration else 1.0
        eased = progress * progress * (3.0 - 2.0 * progress)
        self.amount = self.origin + (self.target - self.origin) * eased
        if progress >= 1:
            self.amount = self.target
        return self.amount

    def set_phase(self, phase):
        if phase == self.phase:
            return
        if phase not in {"ready", "work", "break", "waiting"}:
            raise ValueError("Unknown timer phase")
        self.update()
        self.phase = phase
        target = 1.0 if phase in {"break", "waiting"} else 0.0
        if target == self.target:
            return
        self.origin, self.target = self.amount, target
        self.started = self.clock()
        self.duration = (self.SIT_SECONDS if target else self.STAND_SECONDS) * abs(target - self.origin)

    @property
    def stationary(self):
        return self.phase in {"break", "waiting"} or self.amount > 0.0 or self.target > 0.0

    @property
    def state(self):
        if self.amount != self.target:
            return "sitting_down" if self.target else "standing_up"
        return "seated" if self.amount else "standing"
