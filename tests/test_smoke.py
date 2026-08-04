"""Smoke tests — el sistema arranca."""

import pytest


def test_home_returns_200(anonymous_client):
    response = anonymous_client.get("/")
    assert response.status_code == 200
    assert b"PT-Docs" in response.content


@pytest.mark.django_db
def test_migrations_apply_cleanly():
    """El sólo hecho de que este test corra implica que migrate corrió."""
    from django.contrib.contenttypes.models import ContentType

    assert ContentType.objects.exists()
