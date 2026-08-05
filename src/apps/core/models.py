"""Modelos base: Firma, Usuario, PerfilUsuario."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.mixins import TimestampedModel


class Firma(TimestampedModel):
    """Tenant lógico. Por ahora solo hay una instancia (CR Consultores)."""

    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre")
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmas"

    def __str__(self) -> str:
        return self.nombre


class Usuario(AbstractUser):
    """Usuario del sistema. Pertenece a una Firma."""

    firma = models.ForeignKey(
        Firma,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
        verbose_name="Firma",
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class RolUsuario(models.TextChoices):
    ADMIN_FIRMA = "admin_firma", "Administrador de firma"
    SENIOR = "senior", "Senior"
    JUNIOR = "junior", "Junior"
    REVISOR = "revisor", "Revisor"


class PerfilUsuario(TimestampedModel):
    """Perfil extendido del usuario con rol."""

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario",
    )
    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.JUNIOR,
        verbose_name="Rol",
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self) -> str:
        return f"{self.usuario.username} ({self.get_rol_display()})"
