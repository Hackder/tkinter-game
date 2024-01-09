class SimpleState[T]:
    value: T

    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

    def set(self, value: T):
        self.value = value
