import os

os.environ["KIVY_NO_ARGS"] = "1"
from components.gui.overlay.kivy_only_ui import OverlayApp
from events import Event


class Messenger:
    def send(self, *args, **kwargs):
        print(f"STUB: send {args} {kwargs}")


Event.messenger = Messenger()
OverlayApp().run()
