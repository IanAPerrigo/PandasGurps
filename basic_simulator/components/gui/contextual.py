from os.path import join, dirname

from kivy.properties import OptionProperty, NumericProperty, Property
from kivy.uix.widget import Widget
import kivy

from data_models.actions.movement import MovementType
from events import Event


class DirectionArrow(Widget):
    direction = OptionProperty("None", options=list(map(lambda x: x.name, MovementType)))
    pressed_callback = Property(None)


class MovementTool(Widget):
    def direction_pressed_callback(self, instance, direction):
        event_name = "MOVE_%s" % direction
        Event.signal(event_name)



