from collections.abc import Iterator
from typing import ClassVar

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from sqlalchemy_state_machine import (
    ConfigurationError,
    InvalidTransitionError,
    StateMachine,
    StateMachineMixin,
    Transition,
)

callback_events: list[tuple[str, str]] = []


def record_before(model: object, transition: Transition) -> None:
    callback_events.append((f"before:{transition.name}", str(model.status)))


def record_after(model: object, transition: Transition) -> None:
    callback_events.append((f"after:{transition.name}", str(model.status)))


def raise_after(model: object, transition: Transition) -> None:
    callback_events.append((f"after:{transition.name}", str(model.status)))
    raise RuntimeError("after callback failed")


def raise_before(model: object, transition: Transition) -> None:
    callback_events.append((f"before:{transition.name}", str(model.status)))
    raise RuntimeError("before callback failed")


class Base(DeclarativeBase):
    pass


class Order(StateMachineMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(nullable=False)

    state_machine: ClassVar[StateMachine] = StateMachine(
        state_attribute="status",
        initial="draft",
        transitions=(
            Transition(
                name="submit",
                source="draft",
                target="submitted",
                before=record_before,
                after=record_after,
            ),
            Transition(name="cancel", source=["draft", "submitted"], target="cancelled"),
            Transition(
                name="fail",
                source="submitted",
                target="failed",
                after=raise_after,
            ),
            Transition(
                name="fail_before",
                source="submitted",
                target="failed",
                before=raise_before,
            ),
        ),
    )


@pytest.fixture
def engine() -> Iterator[Engine]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def clear_callback_events() -> None:
    callback_events.clear()


def test_new_instance_uses_initial_state() -> None:
    assert Order().status == "draft"


def test_constructor_state_is_preserved() -> None:
    assert Order(status="submitted").status == "submitted"


def test_can_and_available_transitions_follow_current_state() -> None:
    order = Order()

    assert order.can_transition("submit")
    assert not order.can_transition("missing")
    assert order.available_transitions() == ("submit", "cancel")

    order.transition("submit")

    assert not order.can_transition("submit")
    assert order.can_transition("cancel")
    assert order.available_transitions() == ("cancel", "fail", "fail_before")


def test_transition_changes_state_and_returns_target() -> None:
    order = Order()

    assert order.transition("submit") == "submitted"
    assert order.status == "submitted"


def test_unknown_and_unavailable_transitions_include_action_and_state() -> None:
    order = Order()

    with pytest.raises(InvalidTransitionError, match=r"missing.*draft"):
        order.transition("missing")

    with pytest.raises(InvalidTransitionError, match=r"submit.*submitted"):
        Order(status="submitted").transition("submit")


def test_callbacks_observe_state_before_and_after_transition() -> None:
    order = Order()

    order.transition("submit")

    assert callback_events == [
        ("before:submit", "draft"),
        ("after:submit", "submitted"),
    ]


def test_before_callback_failure_restores_original_state() -> None:
    order = Order(status="submitted")

    with pytest.raises(RuntimeError, match="before callback failed"):
        order.transition("fail_before")

    assert order.status == "submitted"
    assert callback_events == [("before:fail_before", "submitted")]


def test_after_callback_failure_restores_original_state() -> None:
    order = Order(status="submitted")

    with pytest.raises(RuntimeError, match="after callback failed"):
        order.transition("fail")

    assert order.status == "submitted"
    assert callback_events == [("after:fail", "failed")]


def test_loaded_instance_preserves_persisted_state(engine: Engine) -> None:
    with Session(engine) as session:
        order = Order(status="submitted")
        session.add(order)
        session.flush()
        order_id = order.id
        session.commit()
        session.expunge(order)

        loaded = session.get(Order, order_id)

    assert loaded is not None
    assert loaded.status == "submitted"


def test_missing_state_machine_raises_configuration_error() -> None:
    class MissingMachineBase(DeclarativeBase):
        pass

    class MissingMachineOrder(StateMachineMixin, MissingMachineBase):
        __tablename__ = "missing_machine_orders"

        id: Mapped[int] = mapped_column(primary_key=True)
        status: Mapped[str] = mapped_column(nullable=False)

    with pytest.raises(ConfigurationError, match="state_machine"):
        MissingMachineBase.registry.configure()


def test_non_state_machine_declaration_raises_configuration_error() -> None:
    class InvalidMachineBase(DeclarativeBase):
        pass

    class InvalidMachineOrder(StateMachineMixin, InvalidMachineBase):
        __tablename__ = "invalid_machine_orders"

        id: Mapped[int] = mapped_column(primary_key=True)
        status: Mapped[str] = mapped_column(nullable=False)
        state_machine = "invalid"

    with pytest.raises(ConfigurationError, match="state_machine"):
        InvalidMachineBase.registry.configure()


def test_successful_transition_persists_in_transaction(engine: Engine) -> None:
    with Session(engine) as session:
        order = Order()
        session.add(order)
        session.flush()
        order_id = order.id
        assert order.transition("submit") == "submitted"
        session.commit()

    with Session(engine) as session:
        loaded = session.get(Order, order_id)

    assert loaded is not None
    assert loaded.status == "submitted"
