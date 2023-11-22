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

class Transition:
    """
    A utility class for transitioning one float value to another

    Keyword arguments:
    speed -- The speed of the transition in units per second
    duration -- The duration of the transition in seconds
    skip -- If the change in value is greated than skip,
            no transitioning will happen and the value will be set immediately
    easing -- The easing function to use

    At least one of speed or duration must be set
    """
    def __init__(self, *,
                 speed: float|None = None,
                 duration: float|None = 1,
                 skip: float|None = None,
                 easing = Easing.linear):
        self.speed = speed
        self.duration = duration
        self.skip = skip
        self.last_value = None
        self.target_value = None
        self.value = None
        self.progress = 0
        self.distance = 0
        self.easing = easing

    def update(self, value: float, delta_time: float):
        # The first time the transition is updated no transitioning
        # is being done, so we just update the values to reflect the 
        # target at the initial state/value
        if self.last_value is None or self.value is None or self.target_value is None:
            self.last_value = value
            self.target_value = value
            self.value = value
            return value

        if value != self.target_value:
            self.last_value = self.value
            self.target_value = value
            self.distance = value - self.last_value
            self.progress = 0
            if self.skip is not None and self.distance > self.skip:
                self.progress = 1

        if self.progress == 1 or self.distance == 0:
            return value

        if self.speed is not None:
            self.progress += self.speed / self.distance * delta_time
        elif self.duration is not None:
            self.progress += delta_time / self.duration
        else:
            raise Exception('Either speed or duration must be set')

        self.progress = min(self.progress, 1)

        eased_progress = self.easing(self.progress)
        self.value = self.last_value + self.distance * eased_progress

        return (self.value, eased_progress)

