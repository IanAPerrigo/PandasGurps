from panda3d.core import LVector3, LPoint3, PandaNode, TextNode
from direct.fsm import FSM
from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

import random
import numpy as np

from data_models.actions import Action, ActionStatus
from managers.simulation_manager import SimulationStateManager
from managers.action_resolvers import GenericActionResolver
from behaviors import Behavior
from events.actors import RefreshStats


class ActorFSM(FSM.FSM):
    def __init__(self,
                 # Describes the actor and its behavior.
                 data_model, behavior: Behavior,
                 # Managers needed for the FSM to function.
                 simulation_manager: SimulationStateManager,
                 action_resolver: GenericActionResolver):
        FSM.FSM.__init__(self, 'fsm_%r' % data_model.entity_id)

        self.logger = DirectNotify().newCategory(type(self).__name__)
        self.data_model = data_model

        # TODO: Should be derived / configured based on a factory, and allow overriding to support any behavior.
        self.behavior = behavior

        self.yield_turn = None
        self.step_complete = None
        self.simulation_manager = simulation_manager
        self.action_resolver = action_resolver
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

        # Submit the actions to the manager
        actions_arg = args[0]
        self.simulation_manager.action_manager.submit_maneuver(self.data_model.entity_id, actions_arg)

        self.step_complete()

    def exitTakingTurn(self):
        # Unbind the task that calculates the move.
        # TODO: notify the behavior to become inactive (close out any processing its doing)
        taskMgr.remove(self.poll_task)
        self.poll_task = None
        self.yield_turn()

    def poll_behavior(self, task):
        current_state = self.simulation_manager.entity_states[self.data_model.entity_id]

        # TODO: remove this from here, it should be injected to any behavior that needs it without the FSMs concern
        self.behavior.keys = self.keys

        # TODO: allow None as an action that does not re-generate the state so that the behavior can have
        #  its own threaded/async functions that complete eventually.
        taken_actions = self.behavior.act(current_state)

        if taken_actions is not None:
            # Set the actions primary actor.
            taken_actions.set_actor(self.data_model.entity_id)
            self.request('Action', taken_actions)

        return Task.again


class ActorComponent(PandaNode, DirectObject):
    def __init__(self, parent, data_model):
        PandaNode.__init__(self, "%s" % data_model.entity_id)

        self.id = data_model.entity_id
        self.parent = parent
        self.path = parent.attachNewNode(self)
        self.data_model = data_model

        self.health_bar = None

        # Attach event handlers
        RefreshStats.register(self.id, self, self.refresh_stats)

        self._instantiate_self_()

    def refresh_stats(self):
        stats = self.data_model.character_model.stats
        self.health_bar.node().setText("%d/%d" % (stats['CURR_HP'], stats['HP']))

    def _instantiate_self_(self):
        actor = loader.loadModel(self.data_model.model_file)
        actor.reparentTo(self.path)

        # Set the initial position and scale.
        actor.setPos(0, -0.8, 0)
        actor.setScale(1)
        actor.setHpr(180, 0, 0)
        actor.setColor(.5, .5, .5, 0.5)
        actor.setDepthOffset(1)

        text_node = TextNode('health_bar')
        stats = self.data_model.character_model.stats
        text_node.setText("%d/%d" % (stats['CURR_HP'], stats['HP']))
        text_path = actor.attachNewNode(text_node)
        text_path.setScale(0.5)
        text_path.setHpr(180, 0, 0)
        text_path.setColor(1, 1, 1, 1)
        text_path.setPos(1.5, 1, 0.5)
        self.health_bar = text_path
