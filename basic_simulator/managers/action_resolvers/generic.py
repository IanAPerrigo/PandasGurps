from managers import SimulationStateManager
from managers.action_resolver_locator import ActionResolverLocator

from data_models.actions import Action


class GenericActionResolver:
    """
    Locates and dispatches the correct resolver for an action type.
    Fills the dependencies required for each resolver.
    """
    def __init__(self, action_resolver_locator: ActionResolverLocator, simulation_manager: SimulationStateManager):
        # TODO: take all the state objects and managers needed to resolve actions. (simulation_manager, etc.)
        self.action_resolver_locator = action_resolver_locator
        self.simulation_manager = simulation_manager

    def resolve(self, action: Action):
        # Get the applicable resolver container for the action.
        resolver_container = self.action_resolver_locator.resolver(action)

        # Provide the resolver with the current state.
        action_resolver = resolver_container.resolver(simulation_manager=self.simulation_manager)

        action_resolver.resolve(action)


class ActionResolver:
    """ The gist of this class is to extend it and have dependencies related to
    resolving the action be injected
    """
    def __init__(self, simulation_manager: SimulationStateManager):
        self.simulation_manager = simulation_manager
        """"""

    def resolve(self, action):
        raise NotImplementedError()