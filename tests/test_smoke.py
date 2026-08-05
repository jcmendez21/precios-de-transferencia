"""Smoke tests — el sistema arranca."""

import pytest

# test_home_returns_200 removed in Task 8: home now requires login.
# Covered precisely by tests/test_auth.py::test_home_redirects_anonymous_to_login.


@pytest.mark.django_db
def test_migrations_apply_cleanly():
    """El sólo hecho de que este test corra implica que migrate corrió."""
    from django.contrib.contenttypes.models import ContentType

    assert ContentType.objects.exists()
