"""Tests de modelos de catalogos DIAN."""

import pytest
from django.db import IntegrityError


@pytest.mark.django_db
def test_pais_dian_str():
    from apps.catalogos.models import PaisDIAN

    pais = PaisDIAN.objects.create(codigo_dian="249", nombre="Estados Unidos", codigo_iso="US")
    assert str(pais) == "Estados Unidos"


@pytest.mark.django_db
def test_tipo_operacion_has_seccion():
    from apps.catalogos.models import SeccionOperacion, TipoOperacionDIAN

    op = TipoOperacionDIAN.objects.create(
        codigo="21",
        nombre="Venta servicios",
        seccion=SeccionOperacion.INGRESO,
    )
    assert op.seccion == SeccionOperacion.INGRESO


@pytest.mark.django_db
def test_paraiso_fiscal_references_pais():
    from apps.catalogos.models import PaisDIAN, ParaisoFiscal

    pais = PaisDIAN.objects.create(codigo_dian="446", nombre="Islas Caimán", codigo_iso="KY")
    pf = ParaisoFiscal.objects.create(pais=pais)
    assert pf.pais.nombre == "Islas Caimán"


@pytest.mark.django_db
def test_parametro_fiscal_unique_per_anio():
    from apps.catalogos.models import ParametroFiscal

    ParametroFiscal.objects.create(anio=2025, uvt=49799)
    with pytest.raises(IntegrityError):
        ParametroFiscal.objects.create(anio=2025, uvt=50000)
