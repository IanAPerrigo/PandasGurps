from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, NodePath


class Camera:
    def __init__(self, base: ShowBase, config: dict):
        self.base = base
        self.config = config

    def setup(self):
        self.base.set_background_color(self.config.get('background_color'))
        self.base.camLens.setNearFar(1, 100)
        self.base.camLens.setFov(self.config.get('fov'))
        self.base.cam.setPos(self.base.cam.getX() + self.config.get('x_offset'),
                             self.config.get('scroll'),
                             self.base.cam.getZ() + self.config.get('z_offset'))


class Lighting:
    def __init__(self, render: NodePath, config: dict):
        self.render = render
        self.config = config

    def setup(self):
        ambient_light = AmbientLight("ambientLight")
        ambient_light.setColor(self.config.get('ambient_color'))
        directional_light = DirectionalLight("directionalLight")
        directional_light.setDirection(self.config.get('direction'))
        directional_light.setColor(self.config.get('directional_color'))
        directional_light.setSpecularColor(self.config.get('directional_specular_color'))
        # directionalLight.showFrustum()

        self.render.setLight(self.render.attachNewNode(ambient_light))
        self.render.setLight(self.render.attachNewNode(directional_light))

        # Important! Enable the shader generator.
        self.render.setShaderAuto()
