# sqlalchemy-state-machine


[![CI](https://github.com/bigbag/sqlalchemy-state-machine/workflows/CI/badge.svg)](https://github.com/bigbag/sqlalchemy-state-machine/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/bigbag/sqlalchemy-state-machine/branch/main/graph/badge.svg)](https://codecov.io/gh/bigbag/sqlalchemy-state-machine)
[![pypi](https://img.shields.io/pypi/v/sqlalchemy-state-machine.svg)](https://pypi.python.org/pypi/sqlalchemy-state-machine)
[![downloads](https://img.shields.io/pypi/dm/sqlalchemy-state-machine.svg)](https://pypistats.org/packages/sqlalchemy-state-machine)
[![versions](https://img.shields.io/pypi/pyversions/sqlalchemy-state-machine.svg)](https://github.com/bigbag/sqlalchemy-state-machine)
[![license](https://img.shields.io/github/license/bigbag/sqlalchemy-state-machine.svg)](https://github.com/bigbag/sqlalchemy-state-machine/blob/master/LICENSE)

**sqlalchemy-state-machine** is a helper for add transitions functionality in sqlalchemy.


## Installation

sqlalchemy-state-machine is available on PyPI.
Use pip to install:

    $ pip install sqlalchemy-state-machine


## Basic Usage

```py
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_state_machine import StateConfig, StateMixin

Base = declarative_base()

NEW = "new"
SENT = "sent"
FAILED = "failed"

class Event(Base, StateMixin):
    __tablename__ = "users"

    state_config = StateConfig(
        initial=NEW,
        states=[NEW, SENT, FAILED],
        transitions=[
            ["set_sent", NEW, SENT],
            ["set_failed", NEW, FAILED],
        ],
    )

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    status = sa.Column(sa.String(), nullable=False, index=True)


sa.event.listen(Event, "init", Event.init_state_machine)
sa.event.listen(Event, "load", Event.init_state_machine)

event = Event(name="Event1")

assert event.status == NEW
assert event.set_sent()
assert event.status == SENT
```

## License

sqlalchemy-state-machine is developed and distributed under the Apache 2.0 license.

## Reporting a Security Vulnerability

See our [security policy](https://github.com/bigbag/sqlalchemy-state-machine/security/policy).
