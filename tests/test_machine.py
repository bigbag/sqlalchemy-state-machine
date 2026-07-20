from collections.abc import Callable, Hashable

import pytest

from sqlalchemy_state_machine.exceptions import ConfigurationError
from sqlalchemy_state_machine.machine import StateMachine, Transition


def test_transition_normalizes_a_single_source() -> None:
    single = Transition(name="submit", source="draft", target="submitted")

    assert isinstance(single.source, Hashable)
    assert single.source == frozenset({"draft"})
    assert single.sources == frozenset({"draft"})


def test_transition_normalizes_collection_sources() -> None:
    transition = Transition(name="publish", source=["review", "approved"], target="published")

    assert transition.source == frozenset({"review", "approved"})
    assert transition.sources == frozenset({"review", "approved"})


def test_state_machine_preserves_transition_order_and_looks_up_by_name() -> None:
    submit = Transition(name="submit", source="draft", target="review")
    publish = Transition(name="publish", source="review", target="published")
    machine = StateMachine(state_attribute="status", initial="draft", transitions=[submit, publish])

    assert machine.transitions == (submit, publish)
    assert isinstance(machine.transitions, tuple)
    assert machine.transition_named("publish") is publish
    assert machine.transition_named("missing") is None


@pytest.mark.parametrize(
    ("factory", "match"),
    [
        (lambda: Transition(name="", source="draft", target="review"), "name"),
        (lambda: Transition(name="submit", source=[], target="review"), "source"),
        (lambda: Transition(name="submit", source="draft", target=[]), "target"),
        (
            lambda: StateMachine(state_attribute="", initial="draft", transitions=[]),
            "state_attribute",
        ),
        (
            lambda: StateMachine(
                state_attribute="status",
                initial="draft",
                transitions=[
                    Transition(name="submit", source="draft", target="review"),
                    Transition(name="submit", source="review", target="submitted"),
                ],
            ),
            "transition name",
        ),
    ],
)
def test_invalid_declarations_raise_configuration_error(
    factory: Callable[[], object], match: str
) -> None:
    with pytest.raises(ConfigurationError, match=match):
        factory()
