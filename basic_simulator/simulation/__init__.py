

class Simulation:
    def __init__(self):
        self.encounters = []
        self.active_encounter = None

    def add_encounter(self, encounter):
        self.encounters.append(encounter)
