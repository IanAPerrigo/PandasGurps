from kivy.uix.button import Button
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from panda3d_kivy.app import App

from kivy.modules import inspector

from components.gui.contextual import *

kivy.require('1.11.1')


class SidebarContainerLayout(StackLayout):
    direction_pressed_callback = Property(None)


class OverlayApp(App):
    kv_directory = 'components/gui'

    def build(self):
        layout = SidebarContainerLayout()
        return layout
