import numpy as np

from managers import SimulationStateManager
from managers.action_resolvers.generic import ActionResolver
from managers.action_resolvers.decorators import require_consciousness
from data_models.actions.action import ActionStatus
from data_models.entities.stats import StatType


class MovementResolver(ActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(MovementResolver, self).__init__(simulation_manager)

        self.logger = logger

    @require_consciousness
    def resolve(self, action):
        actor = action.actor

        # Validate that number of hexes moved is less than the basic speed of the actor.
        actor_model = self.simulation_manager.being_model_manager.get(actor)
        curr_bm = actor_model.stats[StatType.CURR_BM]
        # TODO: replace hardcoded hex movement cost.
        hex_cost = 1
        if curr_bm - hex_cost < 0:
            action.status = ActionStatus.FAILED
            return

        actor_model.base_stats[StatType.CURR_BM] -= hex_cost

        # TODO: manage movement challenges (terrain difficulty, walls, etc)
        # TODO: in order for this to work, the move resolver must know how much speed it remaining for a given turn.
        #   this also go for other actions, they must know the game state so they can determine whether or not to modify
        #   the game state.

        vec = action.get_vector()
        self.simulation_manager.grid_model.move(action.actor, np.array(vec))
        action.status = ActionStatus.RESOLVED
