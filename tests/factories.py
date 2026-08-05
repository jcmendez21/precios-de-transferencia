"""Factories globales para tests."""

import factory
from django.contrib.auth import get_user_model

from apps.core.models import Firma, PerfilUsuario, RolUsuario


class FirmaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Firma

    nombre = factory.Sequence(lambda n: f"Firma {n}")
    nit = factory.Sequence(lambda n: f"9001234{n:03d}")
    activa = True


class UsuarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@test.co")
    firma = factory.SubFactory(FirmaFactory)


class PerfilUsuarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PerfilUsuario

    usuario = factory.SubFactory(UsuarioFactory)
    rol = RolUsuario.JUNIOR
