import sqlalchemy_state_machine as state_machine


def test_public_api_has_expected_version_and_exports() -> None:
    assert state_machine.__version__ == "2.0.0"
    assert state_machine.__all__ == [
        "ConfigurationError",
        "InvalidTransitionError",
        "StateMachine",
        "StateMachineMixin",
        "Transition",
        "__version__",
    ]
