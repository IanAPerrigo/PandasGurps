from . import SimulationStateManager, ConsciousnessRequiredActionResolver, np
from data_models.actions.action import ActionStatus
from data_models.actors.stats.stat_set import StatType


class MovementResolver(ConsciousnessRequiredActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(MovementResolver, self).__init__(simulation_manager)

        self.logger = logger

    def resolve(self, action):
        super(MovementResolver, self).resolve(action)

        if action.status == ActionStatus.FAILED:
            return
        
        actor = action.actor

        # Validate that number of hexes moved is less than the basic speed of the actor.
        actor_model = self.simulation_manager.entity_model_manager[actor].character_model
        curr_bm = actor_model.stats[StatType.CURR_BM.value]
        # TODO: replace hardcoded hex movement cost.
        hex_cost = 1
        if curr_bm - hex_cost < 0:
            action.status = ActionStatus.FAILED
            return

        actor_model.base_stats[StatType.CURR_BM.value] -= hex_cost

        # TODO: manage movement challenges (terrain difficulty, walls, etc)
        # TODO: in order for this to work, the move resolver must know how much speed it remaining for a given turn.
        #   this also go for other actions, they must know the game state so they can determine whether or not to modify
        #   the game state.

        vec = action.get_vector()
        self.simulation_manager.grid_model.move(action.actor, np.array(vec))
        action.status = ActionStatus.RESOLVED
