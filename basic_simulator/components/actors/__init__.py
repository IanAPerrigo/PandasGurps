from panda3d.core import LVector3, LPoint3, PandaNode
from direct.fsm import FSM
from direct.directnotify.DirectNotify import DirectNotify
from direct.task import Task

import random
import numpy as np

from data_models import actions
from managers.simulation_manager import SimulationStateManager
from behaviors.actors import RandomActorBehavior, HumanPlayerBehavior


class ActorFSM(FSM.FSM):

    def __init__(self, data_model, simulation_manager: SimulationStateManager):
        FSM.FSM.__init__(self, 'fsm_%r' % data_model.entity_id)

        self.logger = DirectNotify().newCategory(type(self).__name__)
        self.data_model = data_model

        # TODO: Should be derived / configured based on a factory, and allow overriding to support any behavior.
        self.behavior = RandomActorBehavior()

        self.yield_turn = None
        self.step_complete = None
        self.simulation_manager = simulation_manager
        self.poll_task = None
        self.keys = None # TODO: Replace with key manager later

    """
    Configuration of the actor.
    """
    def enterActorSetup(self, *args):
        # TODO: call behavior factory (can override the factory by overriding this function)
        pass

    def filterActorSetup(self, request, args):
        pass

    def exitActorSetup(self):
        pass

    """
    Wait for an event from the world.
    """
    def enterWaitForTurn(self, *args):
        pass

    def filterWaitForTurn(self, request, args):
        # TODO: args should contain everything needed for the turn.
        # Required: yield callback for the controlling FSM
        # Required: Managers to interact with the environment.

        if request == 'TakingTurn':
            return 'TakingTurn'

    def exitWaitForTurn(self):
        pass

    """
    Take a turn.
    """
    def enterTakingTurn(self, *args):
        """
        Interact with managers to pull subjective information for this turn.
        Create the behavior object for this actor, and start its internal processing task.
        :param args:
        :return:
        """
        self.simulation_manager.generate_subjective_state_for(self.data_model.entity_id)

        # Schedule a polling loop for
        self.poll_task = taskMgr.add(self.poll_behavior, "wait_for_action")

    def filterTakingTurn(self, request, args):
        # TODO: determine if the actor has remaining actions.
        # STUB:
        has_actions_left = True

        # Handle completion for the turn.
        if request == 'Complete' or not has_actions_left:
            return 'WaitForTurn'

        # TODO: replace the resolving of actions here to a call to the action
        #  manager to store them for later resolving.

        # TODO: Replace with action resolvers
        if isinstance(args[0], actions.MovementAction):
            # TODO: interact with environment based on action returned.
            vec = args[0].get_vector()
            self.simulation_manager.grid_model.move(self.data_model.entity_id, np.array(vec))

        # TODO: generate new state for the next step
        self.simulation_manager.generate_subjective_state_for(self.data_model.entity_id)

        self.step_complete()

    def exitTakingTurn(self):
        # Unbind the task that calculates the move.
        taskMgr.remove(self.poll_task)
        self.poll_task = None
        self.yield_turn()

    def poll_behavior(self, task):
        current_state = self.simulation_manager.entity_states[self.data_model.entity_id]

        # TODO: remove this from here, it should be injected to any behavior that needs it without the FSMs concern
        self.behavior.keys = self.keys
        action = self.behavior.act(current_state)

        self.request('Action', action)
        return Task.again


class ActorComponent(PandaNode):
    def __init__(self, parent, data_model):
        PandaNode.__init__(self, "%s" % data_model.entity_id)

        self.id = data_model.entity_id
        self.parent = parent
        self.path = parent.attachNewNode(self)
        self.data_model = data_model
        self._instantiate_self_()

    def _instantiate_self_(self):
        actor = loader.loadModel(self.data_model.model_file)
        actor.reparentTo(self.path)

        # Set the initial position and scale.
        actor.setPos(0, -0.8, 0)
        actor.setScale(1)
        actor.setHpr(180, 0, 0)
        actor.setDepthOffset(1)