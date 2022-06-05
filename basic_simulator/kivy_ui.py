from kivy.uix.button import Button
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from panda3d_kivy.app import App
from kivy.app import App as KivyOnlyApp
from kivy.lang import Builder

from kivy.modules import inspector

from components.gui.contextual import *

kivy.require('2.0.0')


class SidebarContainerLayout(StackLayout):
    direction_pressed_callback = Property(None)


class OverlayApp(App):
    kv_directory = 'components/gui'

    def build(self):
        layout = SidebarContainerLayout()
        return layout
