

class ActionResolverLocator:
    """
    Wrapper to create a resolver for a given action type.
    """
    def __init__(self, resolvers_for_type: dict):
        self.__resolvers = resolvers_for_type

    def resolver(self, action):
        resolver_container = self.__resolvers.get(type(action))
        if resolver_container is None:
            raise Exception("Cannot locate resolver container for action type.")
        # TODO: maybe have all resolver containers have just a 'resolver' field
        # but still need to wire in the relevant game data (maybe come from the container for this class,
        # and pass the data to the resolver)
        return resolver_container
