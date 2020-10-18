from . import SimulationStateManager, ActionResolver, np


class MovementResolver(ActionResolver):

    # TODO: All state related managers (Grid, Actor, Environment, etc)

    def __init__(self, simulation_manager: SimulationStateManager, logger):
        super(MovementResolver, self).__init__(simulation_manager)

        self.logger = logger

    def resolve(self, action):

        # TODO: manage movement challenges (terrain difficulty, walls, etc)
        # TODO: in order for this to work, the move resolver must know how much speed it remaining for a given turn.
        #   this also go for other actions, they must know the game state so they can determine whether or not to modify
        #   the game state.

        vec = action.get_vector()
        self.simulation_manager.grid_model.move(action.actor, np.array(vec))
