"""Typed declarations for state-machine transitions."""

from collections.abc import Callable, Collection, Hashable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TypeAlias

from .exceptions import ConfigurationError

Callback: TypeAlias = Callable[[object, "Transition"], None]


@dataclass(frozen=True, slots=True)
class Transition:
    """A named transition from one or more source states to a target state."""

    name: str
    source: Hashable | Collection[Hashable]
    target: Hashable
    before: Callback | None = None
    after: Callback | None = None
    sources: frozenset[Hashable] = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ConfigurationError("transition name must be a non-blank string")
        try:
            hash(self.target)
        except TypeError as error:
            raise ConfigurationError("transition target must be hashable") from error

        sources = self._normalized_sources()
        object.__setattr__(self, "source", sources)
        object.__setattr__(self, "sources", sources)

    def _normalized_sources(self) -> frozenset[Hashable]:
        source = self.source
        if isinstance(source, Hashable):
            try:
                hash(source)
            except TypeError:
                pass
            else:
                return frozenset((source,))

        if not isinstance(source, Collection):
            raise ConfigurationError("transition source must be hashable or a collection")
        try:
            sources = frozenset(source)
        except TypeError as error:
            raise ConfigurationError(
                "transition sources must contain only hashable values"
            ) from error
        if not sources:
            raise ConfigurationError("transition source collection cannot be empty")
        return sources


@dataclass(frozen=True, slots=True)
class StateMachine:
    """An immutable collection of transitions for a model state attribute."""

    state_attribute: str
    initial: Hashable
    transitions: Collection[Transition]
    _transitions_by_name: Mapping[str, Transition] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.state_attribute, str) or not self.state_attribute.isidentifier():
            raise ConfigurationError("state_attribute must be a valid identifier")
        try:
            hash(self.initial)
        except TypeError as error:
            raise ConfigurationError("initial state must be hashable") from error
        if not isinstance(self.transitions, Collection):
            raise ConfigurationError("transitions must be a collection of Transition objects")

        transitions = tuple(self.transitions)
        if not all(isinstance(transition, Transition) for transition in transitions):
            raise ConfigurationError("transitions must contain only Transition objects")

        transitions_by_name: dict[str, Transition] = {}
        for transition in transitions:
            if transition.name in transitions_by_name:
                raise ConfigurationError("transition names must be unique")
            transitions_by_name[transition.name] = transition

        object.__setattr__(self, "transitions", transitions)
        object.__setattr__(self, "_transitions_by_name", MappingProxyType(transitions_by_name))

    def transition_named(self, name: str) -> Transition | None:
        """Return the transition declared with *name*, if any."""
        return self._transitions_by_name.get(name)
