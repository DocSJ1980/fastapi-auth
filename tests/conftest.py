"""
Imports the pytest module, which is a popular testing framework for Python.
"""

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlmodel import Session, SQLModel, create_engine

from fastapi_todo_app import settings
from fastapi_todo_app.main import app, get_session
from fastapi_todo_app.models.todo_model import Todo
from fastapi_todo_app.models.user_model import User

"""
Creates a SQLModel engine for the test database, using the connection string from the application settings. The engine is configured with the following options:

- `connect_args={"sslmode": "require"}`: Requires SSL mode for the database connection.
- `pool_recycle=300`: Recycles database connections after 300 seconds of inactivity.
- `pool_size=5`: Sets the connection pool size to 5 connections.
- `echo=True`: Enables SQL statement logging for debugging purposes.

Additionally, a CryptContext instance is created for hashing passwords using the bcrypt algorithm.
"""
connection_string = str(settings.TEST_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(
    connection_string,
    connect_args={"sslmode": "require"},
    pool_recycle=300,
    pool_size=5,
    echo=True,
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


"""
A pytest fixture that creates a new database session for each test module.

This fixture drops and recreates the SQLModel metadata for the test database, ensuring a clean slate for each test module. It then yields a new database session that can be used by the tests.

The fixture has a scope of "module", meaning it will be executed once per test module. The `autouse=True` parameter ensures the fixture is automatically applied to all tests in the module.
"""


@pytest.fixture(scope="module", autouse=True)
def get_db_session():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield Session(engine)


"""
A pytest fixture that creates a test client for the FastAPI application, with the database session overridden to use a test session.

This fixture is marked as `autouse=True`, meaning it will be automatically applied to all tests in the module. It creates a new database session using the `get_db_session` fixture, and then overrides the `get_session` dependency in the FastAPI application to use this test session. Finally, it creates a TestClient instance for the FastAPI application and yields it, allowing the tests to use the test client to make requests to the application.
"""


@pytest.fixture(autouse=True)
def test_app(get_db_session):
    def test_session():
        yield get_db_session

    app.dependency_overrides[get_session] = test_session
    with TestClient(app=app) as client:
        yield client


"""
A pytest fixture that creates a test user in the database for each test module.

This fixture creates a new `User` instance with the email "test@example.com", username "testuser", and a hashed password of "testpassword". It adds the user to the database session and commits the changes.

After the tests in the module have completed, the fixture deletes any `Todo` objects associated with the test user, deletes the test user, commits the changes, and closes the database session.

This fixture is marked as `autouse=True`, meaning it will be automatically applied to all tests in the module. It ensures that a test user is available for any tests that require authentication or user-specific data.
"""


@pytest.fixture(autouse=True)
def create_test_user(get_db_session):
    test_user = User(
        email="test@example.com",
        username="testuser",
        password=pwd_context.hash("testpassword"),
    )
    get_db_session.add(test_user)
    get_db_session.commit()
    yield test_user

    get_db_session.query(Todo).filter(Todo.user_id == test_user.id).delete()
    get_db_session.delete(test_user)
    get_db_session.commit()
    get_db_session.close()


"""
A pytest fixture that generates an access token for a test user.

This fixture logs in the test user with the username "testuser" and password "testpassword", and returns the access token from the login response. This access token can be used in other tests to authenticate requests as the test user.
"""


@pytest.fixture
def auth_token(test_app):
    login_response = test_app.post(
        "/token", data={"username": "testuser", "password": "testpassword"}
    )
    access_token = login_response.json()["access_token"]
    return access_token
