"""Exceptions raised when declaring state machines."""


class ConfigurationError(ValueError):
    """Raised when a state-machine declaration is invalid."""


class InvalidTransitionError(RuntimeError):
    """Raised when an attempted state transition is not permitted."""
