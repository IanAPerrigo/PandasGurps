from typing import List, Set


class DeltaContainer(List[Set]):
    pass


class DeltaObject:
    def __init__(self):
        self._delta_seq_num = -1
        self.current_delta_seq_num = 0
        self._deltas = DeltaContainer()

        # Create the first step.
        self._next()

    def _add(self, delta):
        """
        Add a delta to the internal storage.
        :param delta:
        :return:
        """
        self._deltas[self._delta_seq_num].add(delta)

    def _next(self):
        self._delta_seq_num += 1
        self._deltas.append(set())

    def all(self):
        """
        Return all the deltas up to the current point in time.
        :return:
        """
        complete_set = set()
        delta_sets = self._deltas[self.current_delta_seq_num:self._delta_seq_num]

        # Collect all the sets.
        for s in delta_sets:
            complete_set.union(s)

        self.current_delta_seq_num = self._delta_seq_num

        return complete_set
