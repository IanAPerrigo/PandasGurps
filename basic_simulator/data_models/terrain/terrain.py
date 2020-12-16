

class Terrain:
    """
    Model describing the terrain of a given tile. Terrain can contain different modifiers related to the entities
    on them, most notably movement reductions and cover.

    Potentially implementable feature is to have height associated with the terrain, making any bonuses derived from
    a difference in height during combat (e.g. Obi-Wan having higher ground than Anakin).
    """
    def __init__(self, elevation=0, modifiers=None):
        """
        Base class has the most fundamental features of a terrain (such as elevation, modifiers)
        """
        self.elevation = elevation
        self.modifiers = [] if modifiers is None else modifiers


class MajorTerrain(Terrain):
    """
    Model describing a terrain feature that takes the majority of the location. Only one can exist on a location at a
    time, and the major terrain determines the appearance of the tile (desert, woods, grass, etc).
    """
    def __init__(self, elevation=0, modifiers=None, color=None):
        super(MajorTerrain, self).__init__(elevation=elevation, modifiers=modifiers)

        self.color = color
