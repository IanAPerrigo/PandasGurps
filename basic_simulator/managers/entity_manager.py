import collections


class EntityModelManager(dict):
    """
    Dictionary of entity models by UUID.
    """
    pass


class EntityFsmManager(dict):
    """
    Dictionary of entity FSMs by UUID.
    """
    pass


class EntityComponentManager(collections.MutableMapping):
    """
    Dictionary of entity components by UUID.
    """
    def __init__(self, *args, entity_model_manager: EntityModelManager, **kwargs):
        self.store = dict()
        self.entity_model_manager = entity_model_manager
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value
        self.entity_model_manager[key] = value.data_model

    def __delitem__(self, key):
        del self.entity_model_manager[key]
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def get_paths(self):
        return {key: entity.path for key, entity in self.items()}
