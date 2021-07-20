from direct.fsm import FSM

from events import Event
from components.simulation.turn_management import TurnManagementFSM
from components.event_handlers.character_creation import CharacterCreator
from behaviors.actors.ai import AiBehavior
from behaviors.actors import HumanPlayerBehavior


class GurpsMain(FSM.FSM):
    def __init__(self, turn_management_fsm: TurnManagementFSM, character_creator: CharacterCreator, logger):
        FSM.FSM.__init__(self, 'fsm_%r' % id(self))

        self.turn_management_fsm = turn_management_fsm
        self.character_creator = character_creator
        self.logger = logger.newCategory(__name__)

        #self.request('PlayAreaLoad')

    def enterPlayAreaLoad(self, *args):
        """
        Loading the play area configures containers with the data required for the simulation.
        An alternative to loading the static play area as seen here, would be to load it from a configuration source
        and fill in all the data here (loading a saved simulation).
        :param args:
        :return:
        """
        self.logger.info("[PlayAreaLoad] entering")

        # TODO: actor setup system (character creation)
        # Initialize all players.

        # food = BasicMealComponentContainer.component()
        # self.entity_component_manager[food.id] = food
        # food.load()
        # self.grid_model.insert((0,0), food.id)

        # TODO: Wire character creator, and generate characters here.
        # for _ in range(3):
        #
        #     stat_set = self.character_creator.generate_stats_via_normals(0.5)
        #     entity_id = BeingModelContainer.entity_id()
        #     actor_model = self.character_creator.generate_full_character(entity_id, modified_stats=stat_set)
        #     # TODO: remove
        #     #   actor_model = self.character_creator.generate_character_via_normals(0.5)
        #
        #
        #     # TODO: have behavior come from container. wire managers, id, etc.
        #     behavior = HumanPlayerBehavior(actor_model.entity_id)
        #     actor_fsm = ActorFsmContainer.fsm(data_model=actor_model,
        #                                       behavior=behavior,
        #                                       action_resolver=self.action_resolver)
        #     actor = ActorComponentContainer.component(data_model=actor_model, fsm=actor_fsm)
        #
        #     self.entity_component_manager[actor.id] = actor
        #
        #     # TODO: move this to a different location (a place that manages what is displayed at what time)
        #     actor.load()
        #
        #     # Signal a stats change.
        #     RefreshStats.signal(actor.id)
        #
        #     actor_fsm.request('WaitForTurn')
        #
        #     loc = (random.randint(0,9), random.randint(0,9))
        #     self.grid_model.insert(loc, actor.id)

        Event.signal("generate_random_character", HumanPlayerBehavior)

        for _ in range(2):
            Event.signal("generate_random_character", AiBehavior)

        Event.signal("notify_grid_update")

        # Trigger the turn management object to bootstrap
        self.turn_management_fsm.request("ManagerSetup")
