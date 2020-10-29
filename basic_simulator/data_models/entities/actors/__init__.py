from data_models.entities.being import Being


class ActorModel:
    """
    A collection of data objects that represents an actor.
    """
    def __init__(self, entity_id, character_model: Being, model_file):
        self.entity_id = entity_id
        self.character_model = character_model
        self.model_file = model_file
