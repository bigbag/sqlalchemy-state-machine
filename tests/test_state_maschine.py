import pytest
from transitions import MachineError

from tests.fixtures import FAILED, NEW, SENT, Event


def test_set_sent(prepare_db):
    event = Event(name="Event1")

    assert event.status == NEW
    assert event.state == NEW

    assert event.set_sent()

    assert event.status == SENT
    assert event.state == SENT


def test_set_failed(prepare_db):
    event = Event(name="Event1")

    assert event.status == NEW
    assert event.state == NEW

    assert event.set_failed()

    assert event.status == FAILED
    assert event.state == FAILED


def test_set_not_valid_status(prepare_db):
    event = Event(name="Event1", status=FAILED)

    assert event.status == FAILED
    assert event.state == FAILED

    with pytest.raises(MachineError):
        assert not event.set_sent()

    assert event.status == FAILED
    assert event.state == FAILED


def test_with_save(prepare_db, session):
    session.add(Event(name="Event1", status=NEW))
    session.commit()

    event = session.query(Event).first()

    assert event.status == NEW
    assert event.state == NEW

    assert event.set_failed()

    assert event.status == FAILED
    assert event.state == FAILED


def test_set_not_valid_status_with_save(prepare_db, session):
    session.add(Event(name="Event1", status=FAILED))
    session.commit()

    event = session.query(Event).first()

    with pytest.raises(MachineError):
        assert not event.set_sent()

    assert event.status == FAILED
    assert event.state == FAILED
