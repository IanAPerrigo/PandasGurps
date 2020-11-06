from dependency_injector import containers, providers
from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.ShowBase import ShowBase

from components.camera.camera import Camera, Lighting
from components.main import GurpsMain
from components.simulation.turn_management import TurnManagementFSM
from components.event_handlers.consciousness import ConsciousnessHandler
from components.event_handlers.character_creation import CharacterCreator
from components.grid import GridComponent


class Components(containers.DeclarativeContainer):
    config = providers.Configuration()
    data_models = providers.DependenciesContainer()
    managers = providers.DependenciesContainer()
    action_resolvers = providers.DependenciesContainer()

    # TODO: change
    logger = DirectNotify()

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

    grid = providers.Singleton(
        GridComponent,
        parent=render,
        data_model=data_models.grid_model_objective,
        entity_component_manager=managers.entity_component_manager
    )

    consciousness_handler = providers.Singleton(
        ConsciousnessHandler,
        being_model_manager=managers.being_model_manager,
        status_effect_manager=managers.status_effect_manager,
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

    character_creator = providers.Singleton(
        CharacterCreator,
        action_resolver=action_resolvers.generic_action_resolver,
        entity_component_manager=managers.entity_component_manager,
        status_effect_manager=managers.status_effect_manager,
        being_factory=data_models.being_model.provider
      )

    main_fsm = providers.Singleton(
        GurpsMain,
        turn_management_fsm=turn_management_fsm,
        character_creator=character_creator,
        logger=logger
      )
