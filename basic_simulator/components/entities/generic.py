from panda3d.core import PandaNode, TextNode
from direct.fsm.FSM import FSM
from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from data_models.entities.entity import Entity


class EntityComponent(PandaNode, DirectObject):
    def __init__(self,
                 parent,
                 data_model: Entity,
                 fsm: FSM,
                 model_file: str):
        # Components are bound to the panda node system via their UUID.
        PandaNode.__init__(self, "%s" % data_model.entity_id)

        # Bind a new node to the hierarchy, and leave it empty.
        self.path = parent.attachNewNode(self)

        # Save information into easily accessible variables.
        self.id = data_model.entity_id
        self.parent = parent
        self.data_model = data_model
        self.fsm = fsm
        self.model_file = model_file

    # TODO: make load and unload part of a component subclass that other entities can share (like grid entry components)
    """
    Method used to load the model, and position it in the world.
    """
    def load(self):
        raise NotImplementedError()

    """
    Method used to unload the model (and cleanup events, and its children).
    """
    def unload(self):
        raise NotImplementedError()
