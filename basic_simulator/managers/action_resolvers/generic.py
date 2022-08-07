from dependency_injector.wiring import Provider

from managers.simulation_manager import SimulationStateManager
from managers.action_resolver_locator import ActionResolverLocator

from data_models.actions import Action


class GenericActionResolver:
    """
    Locates and dispatches the correct resolver for an action type.
    Fills the dependencies required for each resolver.
    """
    def __init__(self, resolvers_for_type):
        self.resolvers_for_type = resolvers_for_type

    def resolve(self, action: Action):
        # Obtain the factory, construct the resolver, and resolve the action.
        resolver_factory = self.resolvers_for_type.get(type(action))
        resolver = resolver_factory.build()
        resolver.resolve(action)


class ActionResolver:
    """ The gist of this class is to extend it and have dependencies related to
    resolving the action be injected
    """
    def __init__(self, simulation_manager: SimulationStateManager):
        self.simulation_manager = simulation_manager
        """"""

    def resolve(self, action):
        raise NotImplementedError()