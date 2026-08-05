"""Carga los catálogos DIAN desde archivos CSV embebidos."""

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.catalogos.models import (
    PaisDIAN,
    ParaisoFiscal,
    ParametroFiscal,
    SectorEconomico,
    TipoOperacionDIAN,
)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class Command(BaseCommand):
    help = "Carga catálogos DIAN (idempotente)."

    def handle(self, *args, **options) -> None:
        self._load_paises()
        self._load_paraisos()
        self._load_tipos_operacion()
        self._load_sectores()
        self._load_parametros()
        self.stdout.write(self.style.SUCCESS("Catálogos cargados."))

    def _load_paises(self) -> None:
        path = DATA_DIR / "paises_dian.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                PaisDIAN.objects.update_or_create(
                    codigo_dian=row["codigo_dian"],
                    defaults={
                        "nombre": row["nombre"],
                        "codigo_iso": row["codigo_iso"],
                    },
                )
        self.stdout.write(f"  · Países: {PaisDIAN.objects.count()}")

    def _load_paraisos(self) -> None:
        path = DATA_DIR / "paraisos_fiscales.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    pais = PaisDIAN.objects.get(codigo_dian=row["codigo_pais_dian"])
                except PaisDIAN.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  · País {row['codigo_pais_dian']} no encontrado, saltando paraíso."
                        )
                    )
                    continue
                ParaisoFiscal.objects.update_or_create(
                    pais=pais,
                    defaults={
                        "fecha_inclusion": date.fromisoformat(row["fecha_inclusion"])
                        if row["fecha_inclusion"]
                        else None,
                        "notas": row.get("notas", ""),
                        "activo": True,
                    },
                )
        self.stdout.write(f"  · Paraísos fiscales: {ParaisoFiscal.objects.count()}")

    def _load_tipos_operacion(self) -> None:
        path = DATA_DIR / "tipos_operacion.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                TipoOperacionDIAN.objects.update_or_create(
                    codigo=row["codigo"],
                    defaults={
                        "nombre": row["nombre"],
                        "seccion": row["seccion"],
                        "activa": True,
                    },
                )
        self.stdout.write(f"  · Tipos de operación: {TipoOperacionDIAN.objects.count()}")

    def _load_sectores(self) -> None:
        path = DATA_DIR / "sectores_ciiu.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                SectorEconomico.objects.update_or_create(
                    codigo_ciiu=row["codigo_ciiu"],
                    defaults={
                        "nombre": row["nombre"],
                        "division": row.get("division", ""),
                    },
                )
        self.stdout.write(f"  · Sectores CIIU: {SectorEconomico.objects.count()}")

    def _load_parametros(self) -> None:
        path = DATA_DIR / "parametros_fiscales.csv"
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ParametroFiscal.objects.update_or_create(
                    anio=int(row["anio"]),
                    defaults={
                        "uvt": int(row["uvt"]),
                        "tasa_referencia": Decimal(row["tasa_referencia"])
                        if row["tasa_referencia"]
                        else None,
                    },
                )
        self.stdout.write(f"  · Parámetros fiscales: {ParametroFiscal.objects.count()}")
