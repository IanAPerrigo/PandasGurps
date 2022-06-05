from kivy.properties import StringProperty, Property, NumericProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

from events import Event


class DrawerView:
    def __init__(self, key: str, items: []):
        self.key = key
        self.items = items


class MenuItem:
    def __init__(self, key: str, text: str, drawer_ref):
        self.key = key
        self.text = text
        self.drawer_ref = drawer_ref


ACTION_DRAWER_MENUS = {
    "root": DrawerView("root", items=[
        MenuItem("MOVE", text="Move", drawer_ref=None),
        MenuItem("ATTACK", text="Attack", drawer_ref=None),
        MenuItem("OBSERVE", text="Observe", drawer_ref=None),
        MenuItem("EAT", text="Move", drawer_ref=None),
        MenuItem("MOVE", text="Move", drawer_ref=None),
        MenuItem("MOVE", text="Move", drawer_ref=None),
    ])
}


class ActionDrawer(StackLayout):
    button_list = ObjectProperty(None)
    i = 0

    # , menu_dict: dict
    #
    def __init__(self, **kwargs):
        super(ActionDrawer, self).__init__(**kwargs)
        # self.menu_dict = menu_dict

    def on_action(self, action_type):
        fq_type = f"actionDrawer_{action_type}"
        Event.signal(fq_type)

        # Template for button creation dynamically
        # new_button = PlayerActionButton(action_type=f'Move{self.i}', action_callback=self.on_action,
        #                                 text=f'Move{self.i}')
        # self.i += 1
        #
        # self.button_list.add_widget(new_button)


class PlayerActionButton(Button):
    action_type = StringProperty('')
    action_callback = Property(None)
    size_hint = (None, None)
    height = NumericProperty(50)
    width = NumericProperty(100)

    def on_press(self):
        print(f'touch event from {self.action_type}')
        self.action_callback(self.action_type)
