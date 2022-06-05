import kivy
from kivy.uix.stacklayout import StackLayout
from kivy.app import App

from components.gui import *

kivy.require('2.0.0')


class SidebarContainerLayout(StackLayout):
    direction_pressed_callback = Property(None)


class OverlayApp(App):
    kv_directory = 'components/gui/overlay'

    def build(self):
        layout = SidebarContainerLayout()
        return layout
