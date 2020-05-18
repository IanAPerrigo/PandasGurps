from dependency_injector import containers, providers
import logging

from managers import simulation_manager, state


class SubjectiveSimulationStateContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="subjective_simulation_state")

    subjective_simulation_state = providers.Factory(state.SubjectiveSimulationState)


class ObjectiveSimulationStateContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="objective_simulation_state")

    objective_simulation_state = providers.Factory(state.ObjectiveSimulationState)


class SimulationManagerContainer(containers.DeclarativeContainer):
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name="simulation_manager")

    simulation_manager = providers.Singleton(simulation_manager.SimulationStateManager)
