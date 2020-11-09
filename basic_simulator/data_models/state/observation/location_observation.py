from uuid import UUID
import numpy as np

from .observation import FuzzyObservation


class LocationObservation(FuzzyObservation):
    def __init__(self, center: np.array, noise: float, subject_id: UUID, target_id: UUID):
        """
        An observation of a particular entities location, with some provided noise parameter.
        The noise will most likely be the stddev (or sigma) around the multivariate normal.
        :param center:
        :param noise:
        :param subject_id:
        :param target_id:
        """
        super(LocationObservation, self).__init__(subject_id=subject_id, target_id=target_id)

        self.center = center
        self.noise = noise

    def collapse_observation(self):
        # Dont collapse multiple times.
        if self.collapsed_value is not None:
            return

        sph_cov = self.noise * np.identity(3)
        sampled_value = np.random.multivariate_normal(self.center, sph_cov)
        self.collapsed_value = np.round(sampled_value).astype(np.int)
