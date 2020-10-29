

class Entity:
    def __init__(self, status_effects: set = None):
        self.status_effects = status_effects if status_effects is not None else set()