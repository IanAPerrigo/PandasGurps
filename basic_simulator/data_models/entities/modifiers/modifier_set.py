from typing import Dict, Set, Any

from .modifier import Modifier


class ModifierSet(Dict[Any, Set[Modifier]]):
    pass

