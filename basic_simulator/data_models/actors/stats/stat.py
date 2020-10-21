

class Stat:
    """
    Value container for a particular stat.
    """
    def __init__(self, value, val_range=None):
        self.value = value
        self.val_range = val_range
