import collections
from uuid import UUID
from typing import Dict

from direct.fsm.FSM import FSM

from components.entities.generic import EntityComponent
from data_models.entities.entity import Entity
from data_models.entities.being import Being


class EntityModelManager(Dict[UUID, Entity]):
    """
    Dictionary of entity models by UUID.
    """
    pass


class BeingModelManager(Dict[UUID, Being]):
    """
    Dictionary of entity models by UUID.
    """
    pass


class EntityFsmManager(Dict[UUID, FSM]):
    """
    Dictionary of entity FSMs by UUID.
    """
    pass


class EntityComponentManager(collections.MutableMapping):
    """
    Dictionary of entity components by UUID.
    """
    def __init__(self, *args,
                 entity_model_manager: EntityModelManager,
                 being_model_manager: BeingModelManager,
                 entity_fsm_manager: EntityFsmManager,
                 **kwargs):
        self.store = dict()
        self.entity_model_manager = entity_model_manager
        self.being_model_manager = being_model_manager
        self.entity_fsm_manager = entity_fsm_manager
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value: EntityComponent):
        self.store[key] = value
        self.entity_model_manager[key] = value.data_model

        # Store FSM (if it exists)
        if value.fsm is not None:
            self.entity_fsm_manager[key] = value.fsm

        if isinstance(value.data_model, Being):
            self.being_model_manager[key] = value.data_model

    def __delitem__(self, key):
        if key in self.entity_model_manager:
            self.entity_model_manager.pop(key)
        if key in self.being_model_manager:
            self.being_model_manager.pop(key)
        if key in self.entity_fsm_manager:
            self.being_model_manager.pop(key)
        self.store.pop(key)

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def get_paths(self):
        return {key: entity.path for key, entity in self.items()}
