from data_models.entities.entity import Entity


class Food(Entity):
    """
    Basic form of sustenance.
    """
    def __init__(self, sustenance_value=1):
        # TODO: determine a way to make these "dont care"

        # TODO: add an "edible" status effect
        super(Food, self).__init__(status_effects=set())
        self.sustenance_value = sustenance_value
