from typing import Callable


class Modifier:
    def __init__(self, mod_func: Callable[[float], float] = None, order=0):
        self.modify = mod_func if mod_func is not None else lambda v: v
        self.order = order
