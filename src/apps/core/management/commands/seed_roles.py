"""Crea los grupos Django que corresponden a los roles del sistema."""
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.core.models import RolUsuario


class Command(BaseCommand):
    help = "Crea los grupos Django para cada rol de usuario (idempotente)."

    def handle(self, *args, **options) -> None:
        for value, label in RolUsuario.choices:
            group, created = Group.objects.get_or_create(name=value)
            verb = "creado" if created else "existente"
            self.stdout.write(f"  · Grupo '{value}' ({label}) — {verb}")
        self.stdout.write(self.style.SUCCESS("Roles sembrados correctamente."))
