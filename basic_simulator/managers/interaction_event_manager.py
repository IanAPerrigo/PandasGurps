from direct.showbase.DirectObject import DirectObject
from events import Event
from functools import partial


class InteractionEventManager(DirectObject):
    def __init__(self, event_types):
        super(InteractionEventManager, self).__init__()

        self.event_instances = dict()

        # Bind to each event type and save an entry in the event dictionary
        for event in event_types:
            self.event_instances[event] = 0
            lmb = partial(self.on_event, event)
            Event.register(event, self, lmb)

    def __del__(self):
        for event in self.event_instances.keys():
            Event.unregister(event, self)

        self.event_instances = None

    def on_event(self, event):
        self.event_instances[event] += 1
