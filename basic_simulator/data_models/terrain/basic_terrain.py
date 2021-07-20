from .terrain import Terrain, MajorTerrain


class GrassTerrain(MajorTerrain):
    def __init__(self, elevation=0, color=(0, 1, 0)):
        super(GrassTerrain, self).__init__(elevation=elevation, color=color)


class WaterTerrain(MajorTerrain):
    def __init__(self, entity_id=None, elevation=0, color=(0, 0, 1)):
        # TODO: impassible modifier
        modifiers = []

        super(WaterTerrain, self).__init__(entity_id=entity_id, elevation=elevation, color=color, modifiers=modifiers)


class CliffTerrain(MajorTerrain):
    def __init__(self, entity_id=None, elevation=0, color=(0, 0, 0)):
        # TODO: impassible modifier
        modifiers = []

        super(CliffTerrain, self).__init__(entity_id=entity_id, elevation=elevation, color=color, modifiers=modifiers)
