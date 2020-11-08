from dependency_injector import containers, providers

from kivy_ui import OverlayApp


class GUI(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()

    overlay_panel = providers.Singleton(
        OverlayApp,
        panda_app=core.show_base
    )
