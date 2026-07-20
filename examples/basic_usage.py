from typing import ClassVar

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from sqlalchemy_state_machine import StateMachine, StateMachineMixin, Transition


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
            Transition(name="submit", source="draft", target="submitted"),
            Transition(
                name="cancel",
                source=("draft", "submitted"),
                target="cancelled",
            ),
        ),
    )


engine = create_engine("sqlite://")
try:
    Base.metadata.create_all(engine)

    order = Order()
    assert order.status == "draft"
    assert order.can_transition("submit")
    assert order.transition("submit") == "submitted"

    with Session(engine) as session:
        session.add(order)
        session.commit()

    with Session(engine) as session:
        reloaded = session.get(Order, 1)
        assert reloaded is not None
        assert reloaded.status == "submitted"
finally:
    engine.dispose()
