from typing import Dict, List, Set

from .status_effects import StatusEffect


class StatusSet:
    """
    Set of status effects. Extends special behavior to assist in common operations.
    """
    def __init__(self):
        self.store = dict()

    def add(self, status: StatusEffect):
        key = type(status)
        if key not in self.store:
            self.store[key] = list()
        self.store[key].append(status)

    def get(self, status_type: type) -> list:
        return self.store.get(status_type)

    def has(self, item: StatusEffect) -> bool:
        return item in self.store[type(item)]

    def is_affected_by(self, status_type: type) -> bool:
        return status_type in self.store

    def remove(self, status: StatusEffect):
        key = type(status)
        if key in self.store:
            self.store[key].remove(status)

        if len(self.store[key]) == 0:
            self.store.pop(key)

    def remove_all(self, status_type: type):
        self.store.pop(status_type)

    def items(self):
        statuses = []
        for status_list in self.store.values():
            statuses.extend(status_list)
        return statuses
