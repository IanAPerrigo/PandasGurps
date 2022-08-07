from typing import NamedTuple, Generic, TypeVar, Type

from managers.action_resolvers.generic import ActionResolver, GenericActionResolver


T = TypeVar("T", bound=ActionResolver)


class ActionResolverFactoryState(NamedTuple):
    resolver_type: Type[T]
    sub_state: any


class ActionResolverFactory(Generic[T]):
    def __init__(self, state: ActionResolverFactoryState[T]):
        self.state = state

    def build(self) -> T:
        return self.state.resolver_type(**self.state.sub_state)


class GenericActionResolverFactoryState(NamedTuple):
    resolvers_for_type: dict[type, ActionResolverFactory]


class GenericActionResolverFactory:
    def __init__(self, state):
        self.state = state

    def build(self):
        return GenericActionResolver(resolvers_for_type=self.state.resolvers_for_type)

