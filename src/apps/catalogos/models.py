"""Catálogos oficiales DIAN."""
from django.db import models

from apps.core.mixins import TimestampedModel


class PaisDIAN(models.Model):
    """Códigos oficiales de país usados por DIAN."""

    codigo_dian = models.CharField(max_length=5, unique=True, verbose_name="Código DIAN")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    codigo_iso = models.CharField(max_length=3, blank=True, verbose_name="Código ISO")

    class Meta:
        verbose_name = "País DIAN"
        verbose_name_plural = "Países DIAN"
        ordering = ("nombre",)

    def __str__(self) -> str:
        return self.nombre


class ParaisoFiscal(TimestampedModel):
    """Países/jurisdicciones catalogados como paraísos fiscales (Decreto 1966/2014)."""

    pais = models.OneToOneField(
        PaisDIAN,
        on_delete=models.PROTECT,
        related_name="paraiso_fiscal",
        verbose_name="País",
    )
    fecha_inclusion = models.DateField(null=True, blank=True, verbose_name="Fecha inclusión")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    notas = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Paraíso fiscal"
        verbose_name_plural = "Paraísos fiscales"

    def __str__(self) -> str:
        return f"{self.pais.nombre} (paraíso fiscal)"


class SeccionOperacion(models.TextChoices):
    INGRESO = "ingreso", "Operación de ingreso"
    EGRESO = "egreso", "Operación de egreso"
    ACTIVO = "activo", "Operación con activos"
    PASIVO = "pasivo", "Operación con pasivos"


class TipoOperacionDIAN(models.Model):
    """Catálogo oficial de tipos de operación con vinculados."""

    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código DIAN")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    seccion = models.CharField(
        max_length=10,
        choices=SeccionOperacion.choices,
        verbose_name="Sección",
    )
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Tipo de operación DIAN"
        verbose_name_plural = "Tipos de operación DIAN"
        ordering = ("codigo",)

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nombre}"


class SectorEconomico(models.Model):
    """Sectores CIIU rev. 4 A.C. (DANE)."""

    codigo_ciiu = models.CharField(max_length=6, unique=True, verbose_name="Código CIIU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    division = models.CharField(max_length=100, blank=True, verbose_name="División")

    class Meta:
        verbose_name = "Sector económico (CIIU)"
        verbose_name_plural = "Sectores económicos (CIIU)"
        ordering = ("codigo_ciiu",)

    def __str__(self) -> str:
        return f"{self.codigo_ciiu} — {self.nombre}"


class ParametroFiscal(models.Model):
    """Parámetros anuales: UVT, tasas de referencia, umbrales."""

    anio = models.PositiveIntegerField(unique=True, verbose_name="Año gravable")
    uvt = models.PositiveIntegerField(verbose_name="Valor UVT (COP)")
    tasa_referencia = models.DecimalField(
        max_digits=6, decimal_places=4, null=True, blank=True,
        verbose_name="Tasa de referencia (%)",
    )

    class Meta:
        verbose_name = "Parámetro fiscal"
        verbose_name_plural = "Parámetros fiscales"
        ordering = ("-anio",)

    def __str__(self) -> str:
        return f"Parámetros {self.anio}"
