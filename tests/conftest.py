import os
from fastapi.testclient import TestClient
import pytest
from app.main import app
from dotenv import load_dotenv
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.database import Model, get_db
from app import models

load_dotenv()

engine = sa.create_engine(os.environ['DATABASE_URL']+'_test')
TestSession = so.sessionmaker(engine)

@pytest.fixture()
def session():
    print('Session fixture ran')
    Model.metadata.drop_all(bind=engine)
    Model.metadata.create_all(bind=engine)
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)