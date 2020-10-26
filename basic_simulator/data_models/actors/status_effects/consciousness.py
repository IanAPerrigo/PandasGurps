from .status_effect import StatusEffect


class Dead(StatusEffect):
    """
    Marking status effect. Has no direct effect on modifiers. Handled externally to the effect.
    """


DEAD = Dead()


class NonExistent(StatusEffect):
    """
    Marking status effect. Has no direct effect on modifiers. Handled externally to the effect.
    """


NON_EXISTENT = NonExistent()


class HangingOnToConsciousness(StatusEffect):
    """
    Marking status effect. Has no direct effect on modifiers. Handled externally to the effect.
    """


HANGING_ONTO_CONSCIOUSNESS = HangingOnToConsciousness()


class Unconscious(StatusEffect):
    """
    Marking status effect. Has no direct effect on modifiers. Handled externally to the effect.
    """


UNCONSCIOUS = Unconscious()
