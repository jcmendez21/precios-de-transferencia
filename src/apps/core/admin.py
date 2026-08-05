"""Admin de la app core."""

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.core.models import Firma, PerfilUsuario, Usuario


@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "activa", "created_at")
    search_fields = ("nombre", "nit")
    list_filter = ("activa",)


def _get_fieldsets() -> Any:
    """Get fieldsets with Firma field added."""
    base = UserAdmin.fieldsets or ()
    return (*base, ("Firma", {"fields": ("firma",)}))


def _get_add_fieldsets() -> Any:
    """Get add_fieldsets with Firma field added."""
    base = UserAdmin.add_fieldsets or ()
    return (*base, ("Firma", {"fields": ("firma",)}))


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "firma", "is_staff", "is_active")
    list_filter = ("firma", "is_staff", "is_active")
    fieldsets = _get_fieldsets()
    add_fieldsets = _get_add_fieldsets()


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol")
    list_filter = ("rol",)
