from ..action_resolver_locator import ActionResolverLocator
from ..simulation_manager import SimulationStateManager

from data_models.actors.status_effects.consciousness import *
from data_models.actions import Action, ActionStatus

import numpy as np


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


class ConsciousnessRequiredActionResolver(ActionResolver):
    def __init__(self, simulation_manager: SimulationStateManager):
        super(ConsciousnessRequiredActionResolver, self).__init__(simulation_manager)

    def resolve(self, action):
        """
        Overwrites the base class behavior to verify that the actor in the action subject is conscious to
        execute the action.
        :param action:
        :return:
        """
        actor_model = self.simulation_manager.entity_model_manager[action.actor].character_model

        if DEAD in actor_model.status_effects or UNCONSCIOUS in actor_model.status_effects:
            action.status = ActionStatus.FAILED
            return


"""
Ideas: 
Resolver returns action as:
Completed:
    Action was successfully applied and state was updated.
Incomplete:
    Returns action that requires the resolution of another action to complete.
    e.g. Original action, MovementAction
    MA -requiring-> RollAction
        Return requested action with a continuation action.
Failed:
    Action failed to execute for a reason (Not the same as a failed roll or negative outcome)

"""