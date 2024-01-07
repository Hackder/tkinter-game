from typing import Callable


type BoundValue[T] = Callable[[], T]
