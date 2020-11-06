from dependency_injector import containers, providers

from kivy_ui import OverlayApp


class GUI(containers.DeclarativeContainer):
    config = providers.Configuration()
    components = providers.DependenciesContainer()

    overlay_panel = providers.Singleton(
        OverlayApp,
        panda_app=components.show_base
    )
