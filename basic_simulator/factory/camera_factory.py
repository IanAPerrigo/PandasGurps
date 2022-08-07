from typing import NamedTuple

from direct.showbase.ShowBase import ShowBase

from components.camera.camera import Camera


class CameraFactoryState(NamedTuple):
    base: ShowBase
    config: dict


def build(state: CameraFactoryState) -> Camera:
    return Camera(
        base=state.base,
        config=state.config
    )
