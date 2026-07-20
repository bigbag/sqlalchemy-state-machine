"""SQLAlchemy model mixin for explicit state transitions."""

from collections.abc import Hashable
from typing import Any, ClassVar, cast

from sqlalchemy import event, inspect

from .exceptions import ConfigurationError, InvalidTransitionError
from .machine import Callback, StateMachine, Transition


def _initialize_state(target: object, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
    """Set a newly constructed model's state when no constructor value was supplied."""
    if not isinstance(target, StateMachineMixin):
        return

    machine = target._machine()
    if getattr(target, machine.state_attribute) is None:
        setattr(target, machine.state_attribute, machine.initial)


class StateMachineMixin:
    """Add a declared :class:`StateMachine` to a SQLAlchemy mapped model."""

    state_machine: ClassVar[StateMachine]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if inspect(cls, raiseerr=False) is not None:
            event.listen(cls, "init", _initialize_state)

    @classmethod
    def __declare_last__(cls) -> None:
        """Validate the state-machine declaration after mapper configuration."""
        machine = cls._machine_for_class()
        mapper = inspect(cls)
        if mapper is None or machine.state_attribute not in mapper.attrs:
            raise ConfigurationError(
                f"{cls.__name__}.{machine.state_attribute} must be a mapped state attribute"
            )

    @classmethod
    def _machine_for_class(cls) -> StateMachine:
        machine = getattr(cls, "state_machine", None)
        if not isinstance(machine, StateMachine):
            raise ConfigurationError(f"{cls.__name__}.state_machine must be a StateMachine")
        return machine

    def can_transition(self, name: str) -> bool:
        """Return whether *name* is declared and available from the current state."""
        transition = self._machine().transition_named(name)
        return transition is not None and self._state() in transition.sources

    def available_transitions(self) -> tuple[str, ...]:
        """Return transition names available from the current state, in declaration order."""
        state = self._state()
        return tuple(
            transition.name
            for transition in self._machine().transitions
            if state in transition.sources
        )

    def transition(self, name: str) -> Hashable:
        """Apply an available transition and return its target state."""
        machine = self._machine()
        state = self._state()
        transition = machine.transition_named(name)
        if transition is None:
            raise InvalidTransitionError(f"unknown transition {name!r} from state {state!r}")
        if state not in transition.sources:
            raise InvalidTransitionError(f"transition {name!r} is unavailable from state {state!r}")

        try:
            self._run_callback(transition.before, transition)
            setattr(self, machine.state_attribute, transition.target)
            self._run_callback(transition.after, transition)
        except BaseException:
            setattr(self, machine.state_attribute, state)
            raise
        return transition.target

    def _machine(self) -> StateMachine:
        return type(self)._machine_for_class()

    def _state(self) -> Hashable:
        return cast(Hashable, getattr(self, self._machine().state_attribute))

    def _run_callback(self, callback: Callback | None, transition: Transition) -> None:
        if callback is not None:
            callback(self, transition)
