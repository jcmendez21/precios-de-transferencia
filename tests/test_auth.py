"""Tests de autenticación."""

import pytest


@pytest.mark.django_db
def test_home_redirects_anonymous_to_login(anonymous_client):
    response = anonymous_client.get("/")
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_authenticated_user_can_see_home(client):
    from tests.factories import UsuarioFactory

    user = UsuarioFactory()
    user.set_password("test1234")
    user.save()
    client.login(username=user.username, password="test1234")
    response = client.get("/")
    assert response.status_code == 200
    assert b"PT-Docs" in response.content
