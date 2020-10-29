
class StatusEffect:
    """
    Contains an internal representation of the effects on an actor.
    For the time being, status effects are either direct modifiers on stats and skills, or just flags
    to mark conditions handled elsewhere.

    Modifiers: stored in a dictionary mapping of [thing modified] -> Modifier
    e.g. StatType.ST -> Modifier() = Direct modifier to ST and everything that used it.
    e.g. SkillType.Longsword -> Modifier() = Modifier to the skill of Longsword and anything that could default from it.
    e.g. SkillBase.DX -> Modifier() = Modifier to Skills based on DX (a concrete example of this would be "Shock").

    Flags: contains no modifiers, identified by the the status effect's type.
    e.g. Unconsciousness: handled in the logic that delegates who's turn it is / what actions can be taken.
    e.g. Death: Used to flag a dead actor, handled similarly to unconsciousness.
    e.g. Aim / Concentrate: Used to mark actors that are the target of aiming, etc. Or maybe flip this, to have the status
    of "Aiming" on the actor that is aiming (and then giving them modifiers conditionally.

    """

    def __init__(self, modifiers: dict = None):
        self.modifiers = modifiers if modifiers is not None else dict()
