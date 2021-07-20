from uuid import UUID

from data_models.entities.entity import Entity


class Water(Entity):
    """
    Basic form of water.
    """
    def __init__(self, entity_id, sustenance_value=1):
        super(Water, self).__init__(entity_id)

        # TODO: add an "drinkable" status effect
        #self.status_effects.add()

        self.sustenance_value = sustenance_value


class Food(Entity):
    """
    Basic form of sustenance.
    """
    def __init__(self, entity_id, sustenance_value=1):
        super(Food, self).__init__(entity_id)

        # TODO: add an "edible" status effect
        #self.status_effects.add()

        self.sustenance_value = sustenance_value
