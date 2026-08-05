"""Tests de modelos de la app core."""
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_firma_str_returns_nombre():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="CR Consultores", nit="900123456")
    assert str(firma) == "CR Consultores"


@pytest.mark.django_db
def test_usuario_belongs_to_firma():
    from apps.core.models import Firma
    User = get_user_model()
    firma = Firma.objects.create(nombre="CR Consultores", nit="900123456")
    user = User.objects.create_user(
        username="jyaya",
        email="j@cr.co",
        password="test123",
        firma=firma,
    )
    assert user.firma == firma


@pytest.mark.django_db
def test_perfil_default_rol_is_junior():
    from apps.core.models import Firma, PerfilUsuario, RolUsuario
    User = get_user_model()
    firma = Firma.objects.create(nombre="CR", nit="900")
    user = User.objects.create_user(username="junior", firma=firma)
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
    assert perfil.rol == RolUsuario.JUNIOR


@pytest.mark.django_db
def test_timestamped_model_sets_created_at():
    from apps.core.models import Firma
    firma = Firma.objects.create(nombre="Test", nit="1")
    assert firma.created_at is not None
    assert firma.updated_at is not None
