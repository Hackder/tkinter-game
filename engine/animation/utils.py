from enum import StrEnum

class AnimationDirection(StrEnum):
    Normal = 'Normal'
    Reversed = 'Reversed'
    Alternate = 'Alternate'

class AnimationEnd(StrEnum):
    End = 'End'
    Start = 'Start'

class Easing:
    @staticmethod
    def linear(t: float):
        return t

    @staticmethod
    def ease_in(t: float):
        return t * t

    @staticmethod
    def ease_out(t: float):
        return t * (2 - t)

    @staticmethod
    def ease_in_out(t: float):
        return t * t * (3 - 2 * t)

class Animation:
    def __init__(self, *,
                 start: float = 0,
                 duration: float,
                 repeat_times: int = 0,
                 direction: AnimationDirection,
                 easing=Easing.linear,
                 finish_callback=None,
                 end=AnimationEnd.Start):
        self.duration = duration
        self.state = start
        self.direction = direction
        self.dir = -1 if direction == AnimationDirection.Reversed else 1
        self.easing = easing
        self.repeat_times = repeat_times
        self.times = 0
        self.finish_callback = finish_callback
        self.end = end
        self.done = False

    def mark_done(self) -> float:
        self.done = True
        if self.finish_callback is not None:
            self.finish_callback()

        if self.end == AnimationEnd.Start:
            return 0
        elif self.end == AnimationEnd.End:
            return 1
        
        return 0

    def process(self, delta_time: float) -> float:
        if self.times >= self.repeat_times and self.repeat_times > 0:
            return self.mark_done()

        self.state += self.duration * delta_time * self.dir

        if self.state >= 0 and self.state <= 1:
            return self.easing(self.state)
            
        if self.state > 1:
            if self.direction == AnimationDirection.Normal:
                self.state = self.state % 1
            elif self.direction == AnimationDirection.Reversed:
                self.state = 1
            elif self.direction == AnimationDirection.Alternate:
                self.state = 1 - (self.state % 1)
                self.dir = -1
            self.times += 1
        elif self.state < 0:
            if self.direction == AnimationDirection.Normal:
                self.state = 0
            elif self.direction == AnimationDirection.Reversed:
                self.state = self.state % 1
            elif self.direction == AnimationDirection.Alternate:
                self.state = 1 - (self.state % 1)
                self.dir = 1
            self.times += 1

        if self.times >= self.repeat_times and self.repeat_times > 0:
            return self.mark_done()

        return self.easing(self.state)


