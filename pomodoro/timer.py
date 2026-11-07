from math import ceil
from time import monotonic


MAX_MINUTES = 180


class PomodoroTimer:
    def __init__(self, work=50, rest=10, clock=monotonic):
        self.work = work
        self.rest = rest
        self.clock = clock
        self.reset()

    @property
    def paused(self):
        return not self.ready_to_start and self.deadline is None

    @property
    def ready_to_start(self):
        return self.phase in ("ready", "waiting")

    @property
    def seconds(self):
        if self.ready_to_start:
            return self.work * 60
        remaining = self.remaining if self.paused else self.deadline - self.clock()
        return max(0, min(self.minutes * 60, ceil(remaining)))

    def _begin(self, phase, now):
        self.phase = phase
        self.minutes = self.work if phase == "work" else self.rest
        self.deadline = now + self.minutes * 60
        return phase

    def advance(self):
        return self._advance(self.clock())

    def _advance(self, now):
        if self.deadline is None or now < self.deadline:
            return None
        if self.phase == "work":
            return self._begin("break", now)
        self.reset()
        self.phase = "waiting"
        return "waiting"

    def toggle(self):
        now = self.clock()
        transition = self._advance(now)
        if transition:
            return transition
        if self.ready_to_start:
            return self._begin("work", now)
        if self.paused:
            self.deadline = now + self.remaining
        else:
            self.remaining = self.deadline - now
            self.deadline = None
        return None

    def reset(self):
        self.phase = "ready"
        self.deadline = None
        self.remaining = 0
        self.minutes = 0
