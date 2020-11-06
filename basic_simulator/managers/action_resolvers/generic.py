from dependency_injector.wiring import Provider

from managers import SimulationStateManager
from managers.action_resolver_locator import ActionResolverLocator

from data_models.actions import Action


class GenericActionResolver:
    """
    Locates and dispatches the correct resolver for an action type.
    Fills the dependencies required for each resolver.
    """
    def __init__(self, resolvers_for_type: dict, simulation_manager: SimulationStateManager):
        self.__resolvers = resolvers_for_type
        self.simulation_manager = simulation_manager

    def resolve(self, action: Action):
        # Obtain the provider, construct it, and resolve the action.
        resolver_provider = self.__resolvers.get(type(action))
        action_resolver = resolver_provider()
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