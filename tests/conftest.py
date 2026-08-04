"""Fixtures compartidas de pytest."""

import pytest


@pytest.fixture
def anonymous_client(client):
    """Cliente HTTP sin login."""
    return client
