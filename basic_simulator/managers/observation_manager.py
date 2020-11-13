from uuid import UUID

from data_models.state.observation.observation import ObservationSet, Observation


class ObservationManager:
    def __init__(self):
        self.observations_by_subject = dict()

    def track_observations(self, subject_id):
        if subject_id in self.observations_by_subject:
            return

        self.observations_by_subject[subject_id] = ObservationSet()

    def add_observation(self, observation: Observation):
        self.observations_by_subject[observation.subject_id].add(observation)

    def get_observations(self, subject_id) -> ObservationSet:
        if subject_id not in self.observations_by_subject:
            self.track_observations(subject_id)
        return self.observations_by_subject.get(subject_id)

    def clear(self, subject_id):
        self.observations_by_subject.pop(subject_id, None)
