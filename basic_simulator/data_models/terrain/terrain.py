

class Terrain:
    """
    Model describing the terrain of a given tile. Terrain can contain different modifiers related to the entities
    on them, most notably movement reductions and cover.

    Potentially implementable feature is to have height associated with the terrain, making any bonuses derived from
    a difference in height during combat (e.g. Obi-Wan having higher ground than Anakin).
    """
    def __init__(self):
        """
        Base class has the most fundamental features of a terrain (such as elevation, modifiers)
        """
        self.elevation = None
        self.modifiers = None

