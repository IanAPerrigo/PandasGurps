from typing import Callable


class Modifier:
    def __init__(self, mod_func: Callable[[float], float], order=0):
        self.modify = mod_func
        self.order = order
