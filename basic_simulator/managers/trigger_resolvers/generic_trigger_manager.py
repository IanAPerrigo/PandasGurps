
class TriggerResolver:
    """
    Interface for resolving triggers (similar to action resolvers)
    """

    def resolve(self, trigger):
        raise NotImplementedError()
