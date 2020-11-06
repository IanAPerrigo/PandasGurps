from dependency_injector import containers, providers


class GenericComponentContainer(containers.DeclarativeContainer):
    entity_component_config = providers.Configuration('config')
