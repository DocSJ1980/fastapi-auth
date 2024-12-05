"""
Imports the `TestClient` class from the `fastapi.testclient` module.

The `TestClient` class is used to create a test client for a FastAPI application, which can be used to make HTTP requests to the application and assert the responses.
"""

from fastapi.testclient import TestClient

from fastapi_todo_app.main import app


# Test1: root endpoint
def test_root():
    """
    Test the root endpoint of the FastAPI application, which should return a "Hello World" message.
    """
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_login_success(test_app):
    """
    Test the successful login functionality of the FastAPI application.

    This test case checks that the application correctly authenticates a user with valid credentials and returns the expected access and refresh tokens.

    Args:
        test_app (TestClient): A test client for the FastAPI application.

    Returns:
        None
    """
    response = test_app.post(
        "/token", data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_failure(test_app):
    """
    Test the failure of the login functionality of the FastAPI application.

    This test case checks that the application correctly returns an error when a user attempts to log in with invalid credentials.

    Args:
        test_app (TestClient): A test client for the FastAPI application.

    Returns:
        None
    """
    response = test_app.post(
        "/token", data={"username": "testuser", "password": "wrongpassword"}
    )
    # Assertions
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


def test_create_todo(test_app, create_test_user, auth_token):
    """
    Test the creation of a new todo item in the FastAPI application.

    This test case checks that the application correctly creates a new todo item with the provided task, and that the created todo item has the expected properties, including the user ID of the authenticated user.

    Args:
        test_app (TestClient): A test client for the FastAPI application.
        create_test_user (User): A fixture that creates a test user.
        auth_token (str): An authentication token for the test user.

    Returns:
        None
    """
    test_todo = {"task": "Test Task"}
    response = test_app.post(
        "/todos/", json=test_todo, headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["task"] == test_todo["task"]
    assert "id" in data
    assert data["user_id"] == create_test_user.id  # Using the fixture directly


def test_get_all_todos(test_app, auth_token):
    """
    Test the retrieval of all todo items in the FastAPI application.

    This test case checks that the application correctly retrieves all todo items that have been created, and that the retrieved todo items include the test todo item that was created as part of the test.

    Args:
        test_app (TestClient): A test client for the FastAPI application.
        auth_token (str): An authentication token for the test user.

    Returns:
        None
    """
    test_todo = {"task": "Get all todos test"}
    # Create todo with authentication
    test_app.post(
        "/todos/", json=test_todo, headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Get todos with authentication
    response = test_app.get(
        "/todos/", headers={"Authorization": f"Bearer {auth_token}"}
    )
    data = response.json()
    print(f"Data: {data}")

    assert response.status_code == 200
    assert len(data) > 0
    assert any(todo["task"] == test_todo["task"] for todo in data)


def test_get_single_todos(test_app, auth_token):
    """
    Test the retrieval of a single todo item in the FastAPI application.

    This test case checks that the application correctly retrieves a single todo item that has been created, and that the retrieved todo item matches the test todo item that was created as part of the test.

    Args:
        test_app (TestClient): A test client for the FastAPI application.
        auth_token (str): An authentication token for the test user.

    Returns:
        None
    """
    test_todo = {"task": "Get Single Todo test"}
    test_todo_id = test_app.post(
        "/todos/", json=test_todo, headers={"Authorization": f"Bearer {auth_token}"}
    ).json()["id"]
    response = test_app.get(
        f"/todos/{test_todo_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["task"] == test_todo["task"]


def test_update_todo(test_app, auth_token):
    """
    Test the updating of a single todo item in the FastAPI application.

    This test case checks that the application correctly updates a single todo item that has been created, and that the updated todo item matches the test todo item that was updated as part of the test.

    Args:
        test_app (TestClient): A test client for the FastAPI application.
        auth_token (str): An authentication token for the test user.

    Returns:
        None
    """
    test_todo = {"task": "Get Single Todo test"}
    test_todo_id = test_app.post(
        "/todos/", json=test_todo, headers={"Authorization": f"Bearer {auth_token}"}
    ).json()["id"]
    updated_test_todo = {"task": "Updated single todo test"}
    response = test_app.put(
        f"/todos/{test_todo_id}",
        json=updated_test_todo,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["task"] == updated_test_todo["task"]


def test_delete_todo(test_app, auth_token):
    """
    Test the deletion of a single todo item in the FastAPI application.

    This test case checks that the application correctly deletes a single todo item that has been created, and that the response indicates the task was successfully deleted.

    Args:
        test_app (TestClient): A test client for the FastAPI application.
        auth_token (str): An authentication token for the test user.

    Returns:
        None
    """
    test_todo = {"task": "Get Single Todo test"}
    test_todo_id = test_app.post(
        "/todos/", json=test_todo, headers={"Authorization": f"Bearer {auth_token}"}
    ).json()["id"]
    delete_response = test_app.delete(
        f"/todos/{test_todo_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert delete_response.status_code == 202
    print(delete_response.content)
    data = delete_response.json()
    assert data["message"] == "Task successfully deleted"
