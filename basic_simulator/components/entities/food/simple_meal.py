from panda3d.core import PandaNode, TextNode
from direct.showbase.DirectObject import DirectObject

from components.entities.generic import EntityComponent
from data_models.entities.energy import Food


class BasicMealComponent(EntityComponent):
    def __init__(self, parent, data_model: Food):
        super(BasicMealComponent, self).__init__(parent, data_model, None, None)

        # Components children to be instantiated on load.
        self.path = None

    def load(self):
        # Load the model and attach it to our node.
        self.path = self.parent.attachNewNode(self)
        food_icon_node = TextNode('food_indicator')
        food_icon_node.setText("F")

        food_icon_path = self.path.attachNewNode(food_icon_node)

        # Configure the location of the model (specific to the model itself).
        food_icon_path.setPos(-0.5, -.1, 0)
        food_icon_path.setScale(1)
        food_icon_path.setHpr(0, 0, 0)
        food_icon_path.setColor(1, 1, 1, 1)
        food_icon_path.setDepthOffset(1)

    def unload(self):
        # Unload the entire node.
        self.path.removeNode()
