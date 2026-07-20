# sqlalchemy-state-machine

Explicit, typed state transitions for SQLAlchemy models.

## Requirements

- Python 3.11+ (CI validates Python 3.11, 3.12, 3.13, and 3.14)
- SQLAlchemy 2.x

## Install

```console
uv add sqlalchemy-state-machine
```

```console
pip install sqlalchemy-state-machine
```

## Quick start

Declare a SQLAlchemy 2.x model and its state machine together:

```python
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
Base.metadata.create_all(engine)

with Session(engine) as session:
    order = Order()
    assert order.status == "draft"
    assert order.can_transition("submit")
    assert order.available_transitions() == ("submit", "cancel")
    assert order.transition("submit") == "submitted"

    session.add(order)
    session.commit()
```

`transition(name)` applies a declared transition and returns its target state.
`can_transition(name)` reports whether a transition is currently available, and
`available_transitions()` returns available names in declaration order. Calling
an unknown or unavailable transition raises `InvalidTransitionError`:

```python
from sqlalchemy_state_machine import InvalidTransitionError

try:
    order.transition("submit")
except InvalidTransitionError:
    pass
```

## Callbacks and transactions

A `Transition` can define `before` and `after` callbacks. Both receive
`(model, transition)`. The `before` callback runs while the model has its
source state, the state is then changed, and the `after` callback runs with the
target state. If either callback raises, the model state is restored to its
original value and the exception is re-raised.

The library changes only the mapped state attribute. It owns no SQLAlchemy
session `flush`, `commit`, or `rollback`; application code controls transaction
boundaries.

## Migrating from 1.x

2.0 is a breaking rewrite for Python 3.11+ and SQLAlchemy 2.x.

| 1.x | 2.0 |
| --- | --- |
| `StateConfig` | `StateMachine` and `Transition` |
| `StateMixin` | `StateMachineMixin` |
| Manual SQLAlchemy init/load events | No longer needed |
| Dynamic `model.set_sent()` | `model.transition("set_sent")` |
| Redundant declared states | Inferred from the initial state and transitions |
| `after_state_change` | Per-transition `before` and `after` callbacks |

The legacy API and its `transitions` dependency were removed; update models to
the explicit 2.0 API rather than mixing 1.x declarations with 2.0 classes.

## Example

Run the standalone example:

```console
uv run python examples/basic_usage.py
```

## Development

```console
uv sync
uv run ruff format --check src tests examples
uv run ruff check src tests examples
uv run mypy src
uv run pytest --cov=sqlalchemy_state_machine
uv build
```

## License

sqlalchemy-state-machine is distributed under the Apache License 2.0.
