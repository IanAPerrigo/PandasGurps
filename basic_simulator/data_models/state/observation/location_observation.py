from uuid import UUID
import numpy as np

from .observation import FuzzyObservation


class LocationObservation(FuzzyObservation):
    __samples = []
    __sample_iter = iter(__samples)

    def __init__(self, center: np.array, noise: float, subject_id, target_id):
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

    @staticmethod
    def get_sample():
        sample = next(LocationObservation.__sample_iter, None)
        if sample is None:
            LocationObservation.__samples = np.random.multivariate_normal(np.array([0,0]), np.identity(2), size=10000)
            LocationObservation.__sample_iter = iter(LocationObservation.__samples)
            sample = next(LocationObservation.__sample_iter)
        return sample

    def collapse_observation(self):
        # Dont collapse multiple times.
        if self.collapsed_value is not None:
            return

        sampled_value = self.center + self.noise * LocationObservation.get_sample()
        self.collapsed_value = np.round(sampled_value).astype(np.int)
