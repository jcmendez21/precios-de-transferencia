"""Admin de la app core."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.core.models import Firma, PerfilUsuario, Usuario


@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "activa", "created_at")
    search_fields = ("nombre", "nit")
    list_filter = ("activa",)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "firma", "is_staff", "is_active")
    list_filter = ("firma", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Firma", {"fields": ("firma",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Firma", {"fields": ("firma",)}),
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol")
    list_filter = ("rol",)
