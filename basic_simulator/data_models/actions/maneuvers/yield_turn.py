from . import Maneuver


class YieldTurnManeuver(Maneuver):
    def __init__(self, actions=None):
        super(YieldTurnManeuver, self).__init__([])
