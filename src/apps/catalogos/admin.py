"""Admin de catalogos DIAN."""

from django.contrib import admin

from apps.catalogos.models import (
    PaisDIAN,
    ParaisoFiscal,
    ParametroFiscal,
    SectorEconomico,
    TipoOperacionDIAN,
)


@admin.register(PaisDIAN)
class PaisDIANAdmin(admin.ModelAdmin):
    list_display = ("codigo_dian", "nombre", "codigo_iso")
    search_fields = ("nombre", "codigo_dian", "codigo_iso")


@admin.register(ParaisoFiscal)
class ParaisoFiscalAdmin(admin.ModelAdmin):
    list_display = ("pais", "fecha_inclusion", "activo")
    list_filter = ("activo",)


@admin.register(TipoOperacionDIAN)
class TipoOperacionDIANAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "seccion", "activa")
    list_filter = ("seccion", "activa")
    search_fields = ("codigo", "nombre")


@admin.register(SectorEconomico)
class SectorEconomicoAdmin(admin.ModelAdmin):
    list_display = ("codigo_ciiu", "nombre", "division")
    search_fields = ("codigo_ciiu", "nombre", "division")


@admin.register(ParametroFiscal)
class ParametroFiscalAdmin(admin.ModelAdmin):
    list_display = ("anio", "uvt", "tasa_referencia")
