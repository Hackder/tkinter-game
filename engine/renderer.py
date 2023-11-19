class FrameContext:
    def __init__(self, *, delta_time: float):
        self.delta_time = delta_time

    def __repr__(self):
        return f"FrameContext(delta_time={self.delta_time})"

    def __eq__(self, other):
        return self.delta_time == other.delta_time
