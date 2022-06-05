from uuid import uuid4

from direct.showbase.DirectObject import DirectObject


class Event:
    messenger = None

    @staticmethod
    def signal(event_name, *args):
        Event.messenger.send("%s" % event_name, sentArgs=list(args))

    @staticmethod
    def register(event_name, source: DirectObject, callback):
        """
        Register an event to the id specified. Generic events will have the event in the messenger set as
        id_event_name
        """
        source.accept("%s" % event_name, callback)

    @staticmethod
    def unregister(event_name, source: DirectObject):
        source.ignore("%s" % event_name)
