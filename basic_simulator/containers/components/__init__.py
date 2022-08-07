from dependency_injector import containers, providers
from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.ShowBase import ShowBase

from components.camera.camera import Camera, Lighting
from components.main import GurpsMainFSM
from components.simulation.turn_management import TurnManagementFSM
from components.event_handlers.consciousness import ConsciousnessHandler
from components.event_handlers.character_creation import CharacterCreator
from components.grid import GridComponent
from components.entities.actors import ActorFSM, ActorComponent


class CoreComponents(containers.DeclarativeContainer):
    config = providers.Configuration()

    show_base = providers.Singleton(
        ShowBase
    )

    render = show_base.provided.render

    camera = providers.Singleton(
        Camera,
        base=show_base,
        config=config.camera
    )

    lighting = providers.Singleton(
        Lighting,
        render=render,
        config=config.lighting
    )


class DirectObjects(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Singleton(
        DirectNotify
    )

    managers = providers.DependenciesContainer()

    consciousness_handler = providers.Singleton(
        ConsciousnessHandler,
        being_model_manager=managers.being_model_manager,
        status_effect_manager=managers.status_effect_manager,
        logger=logger
    )


class Fsm(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Singleton(
        DirectNotify
    )

    managers = providers.DependenciesContainer()
    action_resolvers = providers.DependenciesContainer()

    being = providers.Factory(
        ActorFSM,
        simulation_manager=managers.simulation_manager,
        logger=logger
    )

    turn_management_fsm = providers.Singleton(
        TurnManagementFSM,
        turn_manager=managers.turn_manager,
        action_resolver=action_resolvers.generic_action_resolver,
        simulation_manager=managers.simulation_manager,
        entity_fsm_manager=managers.entity_fsm_manager,
        interaction_event_manager=managers.interaction_event_manager,
        tick_manager=managers.tick_manager,
        logger=logger
      )


class Visual(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()
    fsms = providers.DependenciesContainer()
    data_models = providers.DependenciesContainer()
    managers = providers.DependenciesContainer()

    being = providers.Factory(
        ActorComponent,
        parent=core.render,
        model_file=config.being.model_file
    )

    grid = providers.Singleton(
        GridComponent,
        parent=core.render,
        data_model=data_models.grid_model_objective,
        entity_component_manager=managers.entity_component_manager,
        terrain_factory=data_models.terrain_factory
    )


# class Main(containers.DeclarativeContainer):
#     config = providers.Configuration()
#     logger = providers.Dependency()
#     data_models = providers.DependenciesContainer()
#     managers = providers.DependenciesContainer()
#     action_resolvers = providers.DependenciesContainer()
#     behaviors = providers.DependenciesContainer()
#     visual = providers.DependenciesContainer()
#     fsms = providers.DependenciesContainer()
#
#     character_creator = providers.Singleton(
#         CharacterCreator,
#         action_resolver=action_resolvers.generic_action_resolver,
#         entity_component_manager=managers.entity_component_manager,
#         status_effect_manager=managers.status_effect_manager,
#         being_factory=data_models.being_model.provider,
#         behavior_container=behaviors,
#         being_fsm_factory=fsms.being,
#         being_component_factory=visual.being,
#       )
#
#     main_fsm = providers.Singleton(
#         GurpsMain,
#         turn_management_fsm=fsms.turn_management_fsm,
#         character_creator=character_creator,
#         logger=logger
#       )


class Components(containers.DeclarativeContainer):
    config = providers.Configuration()
    data_models = providers.DependenciesContainer()
    managers = providers.DependenciesContainer()
    action_resolvers = providers.DependenciesContainer()
    behaviors = providers.DependenciesContainer()
    fsms = providers.DependenciesContainer()
    visual = providers.DependenciesContainer()

    logger = providers.Singleton(
        DirectNotify
    )

    # core = providers.Container(
    #     CoreComponents,
    #     config=config.core,
    # )
    #
    # direct_objects = providers.Container(
    #     DirectObjects,
    #     config=config.direct_objects,
    #     managers=managers
    # )
    #
    # fsms = providers.Container(
    #     Fsm,
    #     config=config.fsms,
    #     managers=managers,
    #     action_resolvers=action_resolvers
    # )
    #
    # visual = providers.Container(
    #     Visual,
    #     config=config.visual,
    #     core=core,
    #     fsms=fsms,
    #     data_models=data_models,
    #     managers=managers
    # )

    character_creator = providers.Singleton(
        CharacterCreator,
        simulation_manager=managers.simulation_manager,
        entity_component_manager=managers.entity_component_manager,
        status_effect_manager=managers.status_effect_manager,
        being_factory=providers.Factory(
            data_models.being_model.provider
        ),
        human_behavior_factory=providers.Factory(
            behaviors.human.provider
        ),
        ai_behavior_factory=providers.Factory(
            behaviors.ai.provider
        ),
        being_fsm_factory=providers.Factory(
            fsms.being.provider
        ),
        being_component_factory=providers.Factory(
            visual.being.provider
        ),
      )

    main_fsm = providers.Singleton(
        GurpsMainFSM,
        turn_management_fsm=fsms.turn_management_fsm,
        character_creator=character_creator,
        logger=logger
      )

    # main = providers.Container(
    #     Main,
    #     config=config.main,
    #     logger=logger,
    #     data_models=data_models,
    #     managers=managers,
    #     action_resolvers=action_resolvers,
    #     behaviors=behaviors,
    #     visual=visual,
    #     fsms=fsms
    # )
