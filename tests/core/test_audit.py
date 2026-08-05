"""Tests de auditoría con django-simple-history."""
import pytest


@pytest.mark.django_db
def test_firma_creates_history_on_save():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="CR Test", nit="900")
    assert firma.history.count() == 1
    assert firma.history.first().history_type == "+"


@pytest.mark.django_db
def test_firma_history_on_update():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="CR", nit="900")
    firma.nombre = "CR Consultores"
    firma.save()
    assert firma.history.count() == 2
    latest = firma.history.first()
    assert latest.history_type == "~"
    assert latest.nombre == "CR Consultores"
