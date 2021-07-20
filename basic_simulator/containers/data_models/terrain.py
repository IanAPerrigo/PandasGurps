from typing import Dict
from dependency_injector.providers import Provider
from dependency_injector import containers, providers

from data_models.terrain.basic_terrain import *


class TerrainFactory:
    def __init__(self, types: Dict[type, Provider]):
        self._types = types

    def __call__(self, f_type: type, *args, **kwargs):
        provider = self._types[f_type]
        return provider(*args, **kwargs)


class TerrainDataModels(containers.DeclarativeContainer):
    config = providers.Configuration()

    water_terrain = providers.Factory(
        WaterTerrain
    )

    grass_terrain = providers.Factory(
        GrassTerrain
    )

    cliff_terrain = providers.Factory(
        CliffTerrain
    )
