from events import Event
from uuid import uuid4

from direct.showbase.DirectObject import DirectObject


class RefreshStats:
    @staticmethod
    def signal(id: uuid4, *args):
        """
        Used to signal a component that uses stats to re-draw.
        :return:
        """
        Event.signal("refresh_stats_%s" % id, *args)

    @staticmethod
    def register(id: uuid4, source: DirectObject, callback):
        Event.register("refresh_stats_%s" % id, source, callback)
