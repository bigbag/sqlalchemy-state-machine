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
