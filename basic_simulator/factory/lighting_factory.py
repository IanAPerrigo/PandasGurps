from typing import NamedTuple

from direct.showbase.ShowBase import NodePath

from components.camera.camera import Lighting


class LightingFactoryState(NamedTuple):
    render: NodePath
    config: dict


def build(state: LightingFactoryState) -> Lighting:
    return Lighting(
        render=state.render,
        config=state.config
    )