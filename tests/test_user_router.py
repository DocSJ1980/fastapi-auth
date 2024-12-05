def test_user_root(test_app):
    """
    Test the root endpoint for the user API.

    This test checks that the root endpoint for the user API returns the expected response.
    """

    response = test_app.get("/user/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI todo app User Page"}


def test_register_user_success(test_app):
    """
    Test that a new user can be successfully registered.

    This test checks that the user registration endpoint correctly registers a new user with the provided username, email, and password.
    """

    response = test_app.post(
        "/user/register",
        params={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
        },
    )
    assert response.status_code == 200
    assert "successfully registered" in response.json()["message"]


def test_register_user_duplicate(test_app, create_test_user):
    """
    Test that a user cannot be registered with duplicate credentials.

    This test checks that the user registration endpoint correctly rejects an attempt to register a new user with credentials (username and email) that already exist in the system.
    """
    response = test_app.post(
        "/user/register",
        params={
            "username": create_test_user.username,
            "email": create_test_user.email,
            "password": "testpassword",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with these credentials already exists"


def test_get_user_profile(test_app, auth_token, create_test_user):
    """
    Test that a user can successfully retrieve their own profile information.

    This test checks that the "get user profile" endpoint correctly returns the profile information for the authenticated user, including the username, email, and ID.
    """
    response = test_app.get(
        "/user/me", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    user_data = response.json()
    # Compare with the actual test user data from fixture
    assert user_data["username"] == create_test_user.username
    assert user_data["email"] == create_test_user.email
    assert user_data["id"] == create_test_user.id


def test_get_user_profile_unauthorized(test_app):
    """
    Test that a user cannot access their profile without being authenticated.

    This test checks that the "get user profile" endpoint correctly returns a 401 Unauthorized
    response when the request does not include a valid authentication token.
    """
    response = test_app.get("/user/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_user_profile_invalid_token(test_app):
    """
    Test that a user cannot access their profile with an invalid authentication token.

    This test checks that the "get user profile" endpoint correctly returns a 401 Unauthorized
    response when the request includes an invalid authentication token.
    """
    response = test_app.get(
        "/user/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
