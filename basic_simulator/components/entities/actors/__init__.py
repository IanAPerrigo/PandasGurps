from uuid import UUID

from panda3d.core import PandaNode, TextNode
from direct.fsm import FSM
from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from components.entities.generic import EntityComponent
from managers.simulation_manager import SimulationStateManager
from managers.action_resolvers.generic import GenericActionResolver
from behaviors import Behavior
from events.component.actors import RefreshStats
from data_models.entities.being import Being
from data_models.entities.stats.stat_set import StatType


class ActorFSM(FSM.FSM):
    def __init__(self,
                 # Describes the actor and its behavior.
                 data_model: Being,
                 behavior: Behavior,
                 # Managers needed for the FSM to function.
                 simulation_manager: SimulationStateManager,
                 logger
                 ):
        FSM.FSM.__init__(self, 'fsm_%r' % data_model.entity_id)

        self.logger = logger.newCategory(__name__)
        self.data_model = data_model

        # TODO: Should be derived / configured based on a factory, and allow overriding to support any behavior.
        self.behavior = behavior

        self.yield_turn = None
        self.step_complete = None
        self.simulation_manager = simulation_manager
        self.poll_task = None
        self.keys = None # TODO: Replace with key manager later
        self.current_state = None

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
        self.current_state = self.simulation_manager.entity_states[self.data_model.entity_id]\
            .subjective_simulation_state

        # Schedule a polling loop for
        self.poll_task = taskMgr.add(self.poll_behavior, "wait_for_action")

    def filterTakingTurn(self, request, args):
        # Handle completion for the turn.
        if request == 'Complete':
            return 'WaitForTurn'
        elif request == 'Action':
            # Submit the actions to the manager
            actions_arg = args[0]
            self.simulation_manager.action_manager.submit_maneuver(self.data_model.entity_id, actions_arg)

            self.step_complete()

            # Regenerate the state for the actor.
            self.simulation_manager.generate_subjective_state_for(self.data_model.entity_id)
            self.current_state = self.simulation_manager.entity_states[self.data_model.entity_id]\
                .subjective_simulation_state

    def exitTakingTurn(self):
        # Unbind the task that calculates the move.
        # TODO: notify the behavior to become inactive (close out any processing its doing)
        taskMgr.remove(self.poll_task)
        self.poll_task = None

    def poll_behavior(self, task):
        # TODO: remove this from here, it should be injected to any behavior that needs it without the FSMs concern
        self.behavior.keys = self.keys

        # TODO: allow None as an action that does not re-generate the state so that the behavior can have
        #  its own threaded/async functions that complete eventually.
        taken_actions = self.behavior.act(self.current_state)

        if taken_actions is not None:
            # Set the actions primary actor.
            taken_actions.set_actor(self.data_model.entity_id)
            self.request('Action', taken_actions)

        return Task.again


class ActorComponent(EntityComponent):
    def __init__(self,
                 parent,
                 data_model: Being,
                 fsm: ActorFSM,
                 model_file: str,
                 color: tuple = (.5, .5, .5, 0.5)):
        super(ActorComponent, self).__init__(parent, data_model, fsm, model_file)

        # Components children to be instantiated on load.
        self.health_bar = None
        self.color = color

    def refresh_stats(self):
        stats = self.data_model.stats
        self.health_bar.node().setText("%d/%d" % (stats[StatType.CURR_HP], stats[StatType.HP]))

    def load(self):
        # Load the model and attach it to our node.
        actor = loader.loadModel(self.model_file)  # TODO: maybe do this asynchronously.
        actor.reparentTo(self.path)

        # Configure the location of the model (specific to the model itself).
        actor.setPos(0, 0, 0)
        actor.setScale(1)
        actor.setHpr(0, 0, 0)
        actor.setColor(*self.color)
        actor.setDepthOffset(1)

        # Setup the model's children.
        text_node = TextNode('health_bar')
        stats = self.data_model.stats
        text_node.setText("%d/%d" % (stats[StatType.CURR_HP], stats[StatType.HP]))
        text_path = actor.attachNewNode(text_node)
        text_path.setScale(0.5)
        text_path.setHpr(0, 0, 0)
        text_path.setColor(1, 1, 1, 1)
        text_path.setPos(-0.5, -.1, 0)
        self.health_bar = text_path

        # Attach event handlers
        RefreshStats.register(self.id, self, self.refresh_stats)

    def unload(self):
        # Unload in reverse order. Unregister events.
        RefreshStats.unregister(self.id, self)

        # Unload the entire node.
        self.path.removeNode()
