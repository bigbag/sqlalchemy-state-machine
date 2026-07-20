"""Explicit, typed state transitions for SQLAlchemy models."""

from .exceptions import ConfigurationError, InvalidTransitionError
from .machine import StateMachine, Transition
from .mixin import StateMachineMixin

__version__ = "2.1.0"

__all__ = [
    "ConfigurationError",
    "InvalidTransitionError",
    "StateMachine",
    "StateMachineMixin",
    "Transition",
    "__version__",
]
