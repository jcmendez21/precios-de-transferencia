"""Tests de tasks async."""


def test_ping_returns_pong():
    """Función pura testeable sin async."""
    from apps.core.tasks import ping

    assert ping() == "pong"
