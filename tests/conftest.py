import pytest
import sqlalchemy as sa

from tests.fixtures import Event

engine = sa.create_engine("sqlite://")


@pytest.fixture(scope="function")
def session():
    session = sa.orm.scoped_session(sa.orm.sessionmaker(bind=engine))
    yield session
    session.close()


@pytest.fixture
def prepare_db():
    Event.metadata.create_all(engine)

    session = sa.orm.scoped_session(sa.orm.sessionmaker(bind=engine))
    clean_db(session)
    yield
    clean_db(session)
    session.close()


def clean_db(session):
    session.query(Event).delete()
    session.commit()
