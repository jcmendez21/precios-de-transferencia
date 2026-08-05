"""Tests de seed_catalogos."""

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_seed_catalogos_loads_paises():
    from apps.catalogos.models import PaisDIAN

    call_command("seed_catalogos")
    assert PaisDIAN.objects.count() >= 20  # arranque con al menos 20 países comunes
    assert PaisDIAN.objects.filter(codigo_dian="249").exists()  # Estados Unidos


@pytest.mark.django_db
def test_seed_catalogos_loads_tipos_operacion():
    from apps.catalogos.models import TipoOperacionDIAN

    call_command("seed_catalogos")
    assert TipoOperacionDIAN.objects.count() >= 10


@pytest.mark.django_db
def test_seed_catalogos_loads_parametros_fiscales_2025():
    from apps.catalogos.models import ParametroFiscal

    call_command("seed_catalogos")
    assert ParametroFiscal.objects.filter(anio=2025).exists()


@pytest.mark.django_db
def test_seed_catalogos_is_idempotent():
    from apps.catalogos.models import PaisDIAN

    call_command("seed_catalogos")
    count = PaisDIAN.objects.count()
    call_command("seed_catalogos")
    assert PaisDIAN.objects.count() == count  # no duplica
