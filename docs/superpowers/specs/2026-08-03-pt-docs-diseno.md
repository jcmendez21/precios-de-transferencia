# PT-Docs — Diseño del Sistema

| Campo | Valor |
|---|---|
| **Fecha** | 2026-08-03 |
| **Estado** | Diseño aprobado — pendiente escribir plan de implementación |
| **Autor de la firma** | Juan Yaya (CR Consultores Colombia) |
| **Colaborador técnico** | Claude (asistente) |
| **Nombre del sistema** | PT-Docs (Precios de Transferencia — Documentación) |
| **Objetivo MVP** | Automatizar la generación del Informe Local de Documentación Comprobatoria ante la DIAN (Colombia). |
| **Timeline** | 6-8 semanas para MVP funcional. Campaña de declaración 2025 (jul-sep 2026). |

---

## 1. Alcance y restricciones

### 1.1 Alcance MVP (in-scope)

- Generar el **Informe Local** (Documentación Comprobatoria) de precios de transferencia como archivo `.docx`.
- Soportar el **método TNMM / MTUO** (Margen Neto Transaccional) con los cuatro PLIs más comunes:
  - Margen Operativo (Utilidad Operacional / Ventas Netas)
  - Net Cost Plus / NCP (Ut. Op. / (Costos + Gastos))
  - Berry Ratio (Utilidad Bruta / Gastos Operativos)
  - Margen Bruto (Utilidad Bruta / Ventas)
- Cálculo del **rango intercuartílico** (Q1, mediana, Q3) usando el método de interpolación lineal aceptado por DIAN.
- Evaluación de cumplimiento y cálculo de ajuste hipotético.
- Multi-usuario para firma con más de 5 personas, catálogos compartidos.
- Auditoría completa y versionado de informes generados.

### 1.2 Fuera del alcance MVP (post-MVP)

- Declaración Informativa (Formulario 120) — v1.1.
- Informe Maestro (Master File) — v1.1.
- Reporte País por País (CbCR) — v2.
- Métodos CUP, CA, PR, PU — v1.1 en adelante (CUP prioritario por préstamos).
- OCR de comparables — nunca; captura manual es más segura.
- SaaS multi-tenant activo — v2.
- Integración con bases de datos comerciales de comparables — v2+.

### 1.3 Restricciones no negociables (recopiladas del brainstorming)

1. **Comparables**: seleccionados y descargados manualmente por el equipo fuera del sistema. El software solo procesa lo que se le entrega.
2. **Cifras de comparables**: capturadas manualmente en el sistema. Sin OCR.
3. **Volumen**: firma con >5 usuarios, >50 estudios/año.
4. **Despliegue**: web app en VPS privado de la firma (on-premise). Datos tributarios bajo control físico de CR Consultores.
5. **Plantillas**: múltiples plantillas por sector / tipo de operación. El senior las edita en Word directamente.
6. **Piloto**: primer estudio de referencia = END GAME SAS, período 2025.
7. **Equipo**: hay desarrollador contratado, stack robusto aceptable.

---

## 2. Arquitectura y stack

### 2.1 Stack completo

| Capa | Tecnología | Justificación |
|---|---|---|
| Backend | Python 3.12 + Django 5 | Batteries-included, ORM, Admin, permisos por rol, madurez. |
| Base de datos | PostgreSQL 16 | JSONB para snapshots y catálogos, robusto para datos financieros. |
| Frontend | Templates Django + HTMX + Alpine.js + Tailwind CSS | Interactividad sin SPA. Menor superficie de código en MVP corto. |
| Cálculos | NumPy + Pandas | Cuartiles, estadísticos, series. |
| Docx | docxtpl (Jinja2 sobre docx) + python-docx | Plantillas editables por el senior en Word. |
| Excel | openpyxl + pandas | Parseo del formato oficial DIAN. |
| Auth | django-allauth (local + Google Workspace opcional) | Firma con Google Workspace probablemente. |
| Async | Django-Q2 + Redis | Generación docx no bloquea la UI. |
| Testing | pytest-django, factory-boy, hypothesis, playwright | Ver sección 8. |
| Infra | Docker Compose sobre Ubuntu 22.04 LTS | Portable, simple, backups fáciles. |
| TLS/proxy | Caddy | HTTPS automático con Let's Encrypt. |
| Backups | pg_dump diario cifrado + rsync a bucket S3-compatible (Backblaze B2 / Wasabi) | Bajo costo, seguro. |
| Monitoreo | Sentry (o GlitchTip self-hosted) | Errores no manejados. |

### 2.2 Estructura de despliegue

```
[Caddy] ─→ [Django/Gunicorn] ─→ [Postgres]
                │
                ├─→ [Redis] ←─ [Worker Django-Q]
                │
                └─→ [Volumen local o MinIO] (archivos)
```

### 2.3 Estructura del repositorio

```
pt-docs/
├── src/
│   ├── manage.py
│   ├── config/           # settings, urls, wsgi
│   └── apps/
│       ├── core/         # identidad, tenancy, auditoría
│       ├── catalogos/    # países DIAN, paraísos, tipos operación
│       ├── clientes/     # empresas auditadas, períodos
│       ├── comparables/  # banco global de comparables
│       ├── estudios/     # estudios, operaciones, import xlsx
│       ├── analisis/     # métodos, PLIs, cuartiles
│       └── informes/     # plantillas, generación docx
├── templates/            # base HTML
├── static/
├── tests/
├── docker/
├── pyproject.toml
└── docs/
```

### 2.4 Multi-tenant preparado, no activado

El campo `Firma` existe en todas las tablas pero por ahora hay solo una instancia. Habilitar SaaS multi-tenant en v2 no requiere migraciones estructurales.

---

## 3. Modelo de dominio

### 3.1 Entidades principales

```
Firma (tenant lógico, por ahora único)
  └── Usuario (roles: admin, senior, junior, revisor)
  └── Cliente (empresa auditada, ej. END GAME SAS)
        └── PeriodoFiscal (ej. 2025)
              └── Estudio  ◄─── entidad central
                    ├── DocumentoLegal (archivo PDF adjunto: RUT, cámara, composición accionaria; solo respaldo, no se procesa)
                    ├── EEFFContribuyente (cifras digitadas del período: ventas, costos, gastos, utilidad, activos)
                    ├── Operacion (importadas del xlsx DIAN)
                    │     ├── Vinculado (contraparte)
                    │     ├── TipoOperacion (ref catálogo)
                    │     └── monto, país, ciudad, concepto
                    ├── AnalisisSegmentado (varios por estudio)
                    │     ├── metodo (MTUO en MVP)
                    │     ├── pli
                    │     ├── ParteAnalizada (default: Contribuyente)
                    │     ├── segmento_EEFF_contribuyente
                    │     ├── margen_calculado
                    │     ├── ComparableSeleccionado (snapshot inmutable, N=1..M)
                    │     │     ├── EmpresaComparable (ref catálogo)
                    │     │     ├── EEFFComparable (cifras del período)
                    │     │     └── ajustes_aplicados (JSONB)
                    │     ├── RangoIntercuartilico (Q1, Q2, Q3, min, max)
                    │     ├── ConclusionCumplimiento
                    │     └── AjustePropuesto
                    └── InformeGenerado (versionado v1, v2, ...)
```

### 3.2 Catálogos globales de firma (compartidos)

- `EmpresaComparable` — banco reusable entre estudios.
- `PaisDIAN` — códigos DIAN de países.
- `ParaisoFiscal` — Decreto 1966/2014 y actualizaciones.
- `TipoOperacionDIAN` — catálogo oficial DIAN.
- `SectorEconomico` — CIIU rev. 4 A.C. (DANE).
- `PlantillaInforme` — plantillas docx maestras.
- `ParametroFiscal` — UVT anual, tasas de referencia, umbrales de obligación.

### 3.3 Decisiones de diseño clave

- **Estudio = (Cliente + PeriodoFiscal)** como unidad central. Todo cuelga de él.
- **Catálogo de comparables global a la firma**. Reusable entre estudios del mismo sector.
- **Un Estudio puede tener múltiples `AnalisisSegmentado`** (ej. ventas de servicios + préstamos + regalías = 3 análisis).
- **Regla del snapshot**: datos que participan en un cálculo se copian inmutablemente (`ComparableSeleccionado`, `EEFFComparable` en el análisis). Si mañana editas el catálogo, los estudios cerrados no cambian.
- **`ParteAnalizada`** modelada como campo opcional; MVP asume siempre Contribuyente.
- **Estados del Estudio**: `borrador → en_analisis → en_revision → cerrado → generado_pdf → presentado_dian`. Solo `cerrado` bloquea edición.
- **Versionado del `InformeGenerado`**: cada regeneración crea nueva versión; nunca sobreescribe.
- **Auditoría transversal**: `django-simple-history` o `django-auditlog` sobre entidades sensibles.

---

## 4. Apps Django y responsabilidades

### 4.1 `apps/core/` — Fundaciones
Identidad, tenancy, auditoría, base abstracta de modelos. Ninguna otra app depende hacia arriba; todas dependen hacia abajo de core.

Modelos: `Firma`, `Usuario` (extiende `AbstractUser`), `PerfilUsuario` (rol), `LogAuditoria`. Middleware de audit-trail. Mixin `TimestampedModel`. Grupos: `admin_firma`, `senior`, `junior`, `revisor`.

### 4.2 `apps/catalogos/` — Catálogos DIAN
Tablas maestras estáticas o semi-estáticas. `PaisDIAN`, `ParaisoFiscal`, `TipoOperacionDIAN`, `SectorEconomico`, `ParametroFiscal`. Semillas cargadas al deploy; admin puede actualizar. Solo lectura desde apps operativas.

### 4.3 `apps/clientes/` — Empresas auditadas
CRUD de cliente + período + documentos legales. Depende de core + catalogos.

### 4.4 `apps/comparables/` — Banco global de comparables
`EmpresaComparable`, `EEFFComparable` (por año), `AjusteContable`. Búsqueda por sector/país/tamaño. Formulario de captura de EEFF (una fila por período). Historial multi-año por comparable.

**Control de acceso**: agregar/editar/inactivar `EmpresaComparable` en el catálogo global requiere rol **senior o admin**. El **junior** puede seleccionar comparables existentes y digitar EEFF de un comparable ya creado, pero no crear la ficha del comparable ni cambiar metadata (país, sector, criterio). Esto evita que el catálogo compartido se contamine.

### 4.5 `apps/estudios/` — Expediente del estudio
`Estudio`, `Operacion`. Importador xlsx DIAN (7 hojas del formato oficial: `Op. Vinculados Economicos`, `Op. Prestamos Vinculados Econom`, `Op. Paraisos Fiscales`, `Op. Prestamos Paraisos Fiscales`, `Encuesta país por país`, `Listado Paraisos`, `SEGMENTACION OPERACIONES`). Validación línea a línea con reporte. Edición inline HTMX. Depende de core, catalogos, clientes.

### 4.6 `apps/analisis/` — Corazón matemático
`AnalisisSegmentado`, `ComparableSeleccionado`, `RangoIntercuartilico`, `ConclusionCumplimiento`, `AjustePropuesto`.

Módulo puro `calculos.py` sin side-effects:
- `calcular_pli(eeff, tipo_pli) -> Decimal`
- `calcular_rango_intercuartilico(margenes: list[Decimal]) -> dict` (interpolación lineal DIAN, congelada con test de referencia)
- `evaluar_cumplimiento(margen_pa, rango) -> ConclusionEnum`
- `calcular_ajuste(margen_pa, rango) -> Decimal`

Vistas: crear análisis, seleccionar comparables del catálogo, ejecutar cálculo, ver rango con gráfico.

### 4.7 `apps/informes/` — Plantillas y generación docx
`PlantillaInforme`, `InformeGenerado`. Módulo `renderer.py` y `context_builder.py`. Generación async via Django-Q. Depende de core, estudios, analisis.

### 4.8 Reglas de comunicación entre apps

- Dependencias solo hacia abajo (nunca ciclos).
- Interfaz pública de cada app = `services.py`.
- No importar modelos internos de otras apps directamente en views.
- IDs > referencias directas cuando cruce apps.

---

## 5. User Journey

### 5.1 Fase 0 — Setup (una vez, por admin)
Instalar, migrar, cargar catálogos DIAN, crear usuarios con roles, subir plantillas maestras iniciales validadas. MVP ship con al menos una plantilla operativa: **TNMM — Servicios** derivada del Informe Local END GAME 2024 con marcadores docxtpl insertados.

### 5.2 Fase 1 — Alta cliente y período (~2 min)
Crear `Cliente` (NIT, razón social, sector CIIU) → crear `PeriodoFiscal 2025` → subir documentos legales (respaldo, no procesados).

### 5.3 Fase 2 — Crear Estudio (~30 seg)
Desde ficha del cliente. Estado inicial: `borrador`. Se abre expediente con tabs: Operaciones · Análisis · Comparables · Informe.

### 5.4 Fase 3 — Importar xlsx DIAN (~5 min)
Upload xlsx → sistema detecta 7 hojas → preview de importación con conteo por sección, warnings, errores → confirmar → operaciones creadas → edición inline HTMX si hay que corregir.

### 5.5 Fase 4 — Definir análisis segmentados (5-10 min)
Por cada análisis: nombre, selección de operaciones (multi-select), método (MTUO en MVP), PLI, parte analizada. Múltiples análisis por estudio.

### 5.6 Fase 5 — Segmentar EEFF del contribuyente (5-10 min)
**Paso deliberadamente forzado.** El usuario asigna qué porción de ventas/costos/gastos corresponde a cada análisis. La suma de segmentos + no-vinculado debe cuadrar con el total EEFF (tolerancia 0.1%). Sistema calcula PLI del contribuyente.

### 5.7 Fase 6 — Seleccionar comparables (5-15 min)
Buscar en catálogo global por sector/país. Si no existen, digitar nuevos (quedan reusables). Seleccionar → snapshot inmutable. Ajustes contables opcionales con justificación obligatoria.

### 5.8 Fase 7 — Cálculo automático (~1 seg)
Sistema calcula PLI de cada comparable, ordena, computa Q1/Mediana/Q3 (interpolación lineal DIAN), compara con contribuyente, emite conclusión, calcula ajuste si fuera. UI muestra tabla + gráfico visual del rango + semáforo.

### 5.9 Fase 8 — Revisión senior (asíncrono)
Junior cambia estado a `en_revision` → senior notificado → revisa con comentarios inline → aprueba (`cerrado`) o rechaza (vuelve a `borrador`).

### 5.10 Fase 9 — Generar Informe Local (~30 seg async)
Selector de plantilla sugerida por sector + tipo operación principal → task async carga plantilla, arma contexto, renderiza con docxtpl, inserta gráficos como InlineImage, guarda como `InformeGenerado v1`. Descargable. Regeneraciones → v2, v3.

### 5.11 Fase 10 — Cierre y archivo
Firma y presentación a DIAN → marcar `presentado_dian` → estudio read-only. Data disponible para reuso el año siguiente.

---

## 6. Gestión de plantillas y generación docx

### 6.1 Principio rector

La plantilla es un `.docx` normal, se edita en Word, el software solo la rellena. Si DIAN cambia wording, el senior edita el Word y sube; cero código.

### 6.2 Sintaxis (docxtpl / Jinja2 en Word)

Marcadores dentro del texto Word:
- Variables: `{{ empresa.razon_social }}`, `{{ analisis.rango.q1|pct }}`.
- Loops: `{% for analisis in analisis_segmentados %} ... {% endfor %}`.
- Loops en filas de tabla: `{%tr for c in comparables %} ... {%tr endfor %}`.
- Condicionales: `{% if analisis.ajuste_pesos > 0 %} ... {% endif %}`.
- Imágenes: `{{ analisis.grafico_rango }}` (InlineImage de matplotlib).

### 6.3 ContextBuilder

Función `build_context(estudio) -> dict` en `apps/informes/context_builder.py`. La plantilla nunca ve modelos Django, solo un dict aplanado y estable. Cambios en modelos no rompen plantillas si el ContextBuilder mantiene el contrato.

### 6.4 Filtros custom Jinja

| Filtro | Ejemplo | Resultado |
|---|---|---|
| `\|pct` | `{{ 0.1234\|pct }}` | `12,34%` |
| `\|cop` | `{{ 5000000\|cop }}` | `$ 5.000.000` |
| `\|miles` | `{{ 5000000\|miles }}` | `5.000` |
| `\|fecha_larga` | `{{ dt\|fecha_larga }}` | `31 de diciembre de 2025` |
| `\|nit` | `{{ '900123456'\|nit }}` | `900.123.456-1` |

### 6.5 Modelo `PlantillaInforme`

Campos: `nombre`, `sector_ciiu`, `metodo_default`, `tipos_operacion_aplicables (M2M)`, `archivo_docx`, `version`, `activa`, `contexto_esperado_json`.

### 6.6 Validación al subir plantilla

1. Extraer marcadores `{{ }}` y `{% %}` con docxtpl parsing.
2. Comparar contra contexto canónico.
3. Reportar: válidos, desconocidos (typos), no usados (informativo).
4. Solo si no hay errores críticos, guardar como nueva versión.

### 6.7 MVP = Modo A (plantilla única multi-análisis)

Una plantilla itera sobre todos los análisis del estudio con bloques `{% if analisis.metodo == 'MTUO' %}`. Suficiente para 80% de casos. Modo B (composición de sub-plantillas) queda para v1.1 si se supera cierto umbral de complejidad.

### 6.8 Post-generación

- `InformeGenerado v1` es el output crudo del sistema.
- Usuario puede editar el docx descargado en Word para retoques.
- Puede subir un "Informe Final firmado" como archivo adjunto separado.
- Ambos quedan guardados: el generado y el efectivamente presentado.
- Diff visual entre ambos: v2.

---

## 7. Errores, validaciones y auditoría

### 7.1 Tres capas de validación

- **Capa 1 — Entrada**: en cada form/import antes de guardar. "No dejes basura entrar".
- **Capa 2 — Dominio**: reglas de negocio de PT. "El número está bien digitado pero no tiene sentido económico".
- **Capa 3 — Coherencia**: antes de calcular o generar informe. "El estudio no está listo para este paso".

Toda validación vive en `services.py` como función pura. Invocada desde forms + views + tests. Sin duplicación.

### 7.2 Validaciones críticas del MVP

**Al importar xlsx**:
- NIT solo dígitos, longitud válida.
- País existe en `PaisDIAN`.
- Tipo operación existe en `TipoOperacionDIAN`.
- Monto numérico, no negativo salvo casos permitidos.
- Sección xlsx coherente con tipo operación.
- Filas vacías se ignoran; parciales se marcan `incompleta` y bloquean cierre.

Contrato: `ImportReport` con `{ ok, warnings, errors, detalle[] }`.

**Al capturar EEFF comparable**:
- Todas las cifras del mismo período.
- Moneda declarada.
- Signos económicos válidos.
- Coherencia: `utilidad_operacional ≈ ventas − costos − gastos ± ajustes` (tolerancia 0.5%).
- Ajustes contables requieren justificación obligatoria.

**Al crear `AnalisisSegmentado`**:
- MTUO obliga PLI.
- Contribuyente exige EEFF cargado.
- Al menos una operación seleccionada, todas del mismo estudio.
- No duplicar análisis con mismas operaciones sin justificación.

**Al segmentar EEFF del contribuyente**:
- Suma de segmentos + no-vinculado = total EEFF, tolerancia 0.1%. Bloqueo si no cuadra.
- Cada segmento con ventas > 0 si el PLI lo usa como denominador.

**Al calcular rango**:
- N ≥ 3 comparables (validación mínima estadística).
- N < 5 → warning explícito visible (no bloquea).
- PLI de cada comparable calculable (no div/0, no NaN).
- Mismo período fiscal o justificación.
- Algoritmo de interpolación lineal DIAN congelado en test de referencia.

**Al generar informe**:
- Estudio en `cerrado`.
- Cada análisis con rango calculado y conclusión.
- Plantilla compatible con método usado.
- Dry-run de contexto: todas las variables que la plantilla espera existen.

### 7.3 Jerarquía de errores

```
UserError (esperado, culpa del input)
    ├── ValidationError    → mostrar en form
    ├── ImportError        → reporte, no importar filas malas
    └── BusinessRuleError  → banner, bloquea paso

SystemError (inesperado, culpa nuestra)
    ├── RenderError (docx)  → 500 amigable + Sentry
    ├── CalculationError    → notificar admin, ofrecer reintento
    └── UnhandledException  → 500 genérico + Sentry
```

Regla: no exponer stack traces al usuario. Cada `SystemError` con ID de correlación buscable en logs.

### 7.4 Auditoría

`LogAuditoria` sobre entidades sensibles: `Operacion`, `AnalisisSegmentado`, `ComparableSeleccionado`, `EEFFComparable`, `AjusteContable`, `PlantillaInforme`, `InformeGenerado`, estados del `Estudio`. Guarda timestamp, usuario, IP, valores antes/después (JSON diff).

Trazabilidad del cálculo:
- Cada `RangoIntercuartilico` guarda lista ordenada de PLIs de comparables usados + hash del algoritmo.
- Cada `InformeGenerado` guarda snapshot completo del contexto en `snapshot_datos JSONB` para reproducibilidad.

Vista timeline por estudio filtrable, exportable a CSV/PDF.

### 7.5 Retención y protección

- Estudios cerrados: read-only obligatorio; solo admin reabre con justificación.
- Backups: pg_dump diario cifrado, rotación 30d/12m/5a, copias off-VPS.
- PII no expuesto en logs (filtro logging). NITs y montos solo en DB.
- Passwords: Argon2. Sesiones: SECURE_COOKIE, HTTPS_ONLY.
- Habeas data (Ley 1581/2012): función admin para exportar/eliminar cliente.

---

## 8. Testing y CI/CD

### 8.1 Pirámide

- **E2E (Playwright)**: 5-10 tests. Flujo completo import → cálculo → docx.
- **Integración**: 30-50 tests. Views + DB + services por app.
- **Unitarios**: 150-300 tests. Cálculos, validaciones, filtros, builders.

### 8.2 Rigor por zona

- **Máximo (property-based + Hypothesis)**: `calcular_pli`, `calcular_rango_intercuartilico`, `evaluar_cumplimiento`, `calcular_ajuste`, segmentación EEFF.
- **Alto**: importador xlsx, ContextBuilder, rendering plantilla, validaciones.
- **Medio**: CRUD, permisos, vistas HTMX.
- **Bajo (smoke)**: páginas cargan sin 500.

### 8.3 Cobertura target

- `apps/analisis/`: ≥ 85%.
- Global: ≥ 70%.

### 8.4 Herramientas

pytest-django, pytest-cov, factory-boy, hypothesis, pytest-playwright, pytest-xdist, ruff, mypy, pre-commit.

### 8.5 CI/CD

GitHub Actions (o Gitea self-hosted). Pipeline: lint → mypy → unit → integración → E2E → build Docker → registry. Staging auto desde `develop`, producción manual desde `main` con approval. Migraciones con `--check` previo.

### 8.6 Fixture crítica

Materiales de END GAME 2025 → factory → estudio completo → test E2E `test_end_game_genera_informe_local_correcto` compara docx generado contra referencia aprobada. Regresión rompe merge.

---

## 9. Roadmap y Definition of Done

### 9.1 Sprints del MVP (6-8 semanas)

- **Sprint 0 (sem 1)**: setup repo, Docker, Django, Postgres, CI/CD, core + catalogos, auth con roles.
- **Sprint 1 (sem 2-3)**: apps clientes + estudios, importador xlsx, edición inline. Golden path: cargar xlsx END GAME.
- **Sprint 2 (sem 3-5)**: catálogo comparables, motor `calculos.py` con tests, AnalisisSegmentado, segmentación EEFF, cálculo rango, UI gráfica.
- **Sprint 3 (sem 5-6)**: motor docxtpl, ContextBuilder, admin plantillas, convertir Informe Local END GAME 2024 en plantilla, generación async. Golden path: END GAME 2025 → docx validado.
- **Sprint 4 (sem 6-8)**: auditoría completa, revisión senior + notificaciones, versionado informes, backups, manual usuario.

### 9.2 Definition of Done del MVP

1. Junior carga xlsx END GAME y ve operaciones importadas sin errores.
2. Junior crea AnalisisSegmentado MTUO con PLI Margen Operativo.
3. Sistema calcula Q1/Mediana/Q3 sobre 19 comparables de END GAME **coincidiendo con estudio manual**.
4. Sistema genera docx del Informe Local desde plantilla convertida, **igual o mejor** que el manual.
5. Senior puede revisar y aprobar antes de generar informe.
6. Toda acción sensible en auditoría.
7. Backups probados con restore en staging.
8. Suite tests pasa en CI, cobertura ≥ 85% en `apps/analisis`.
9. Se procesa END GAME 2025 real end-to-end y el docx es presentable a DIAN.

### 9.3 Post-MVP

**v1.1** (después campaña 2025):
- Método CUP (préstamos + regalías).
- Master File.
- Formulario 120 (XML para MUISCA).
- Vista comparativa año/año.

**v1.2**:
- Métodos CA, PR, PU.
- Dashboard ejecutivo con semáforos y alertas de vencimientos.
- Analytics de márgenes por sector.

**v2**:
- SaaS multi-tenant activo.
- SSO Google Workspace / Microsoft.
- Diff visual docx generado vs firmado.
- Integración con TP Catalyst API u otras.
- App móvil revisores.

### 9.4 Deuda técnica registrada

- Importador xlsx asume formato exacto DIAN 2025; layout changes → actualización manual. Mitigación: parser configurable en v1.2.
- Modo A de plantillas puede complicarse con >3 métodos; migración a Modo B planeada en v1.1.
- Catálogo de comparables sin conexión a fuente externa; mantenimiento manual (aceptable para firma mediana).

---

## 10. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación |
|---|---|---|---|
| Formato xlsx DIAN cambia mid-campaña | Alto | Media | Parser tolerante a columnas extra; test de importación contra ejemplos oficiales cada release. |
| Plantilla docx corrupta bloquea generación | Alto | Baja | Validación al subir; versión anterior sigue activa; capturar `UndefinedError` con mensaje legible. |
| Cálculo de cuartiles diverge del método DIAN | Muy alto | Baja | Test de referencia contra ejemplo publicado; property-based tests; congelar algoritmo con hash. |
| Falta capacitación del equipo → uso incorrecto | Medio | Alta | Fase 5 (segmentación EEFF) forzada; warnings visibles; manual básico dentro de la app. |
| Datos tributarios expuestos por incidente | Muy alto | Baja | On-premise, cifrado en reposo (LUKS), backups cifrados fuera de VPS, no PII en logs. |
| Timeline 6-8 semanas insuficiente | Alto | Media | Golden path END GAME desde sprint 1; corte de features no críticos si aparece slippage. |
| Piloto END GAME no valida el diseño | Alto | Baja | Testing paralelo con caso real; senior valida output docx antes de considerar MVP hecho. |

---

## 11. Preguntas abiertas y decisiones diferidas

Ninguna bloqueante para escribir el plan de implementación. Se listan para retomar en plan/implementación:

- **Google Workspace SSO**: activar en Sprint 0 o dejar solo login local para MVP y activar en Sprint 4. Decisión menor.
- **Notificaciones (Fase 8 revisión senior)**: email + in-app, o solo in-app. Sugerencia: email + in-app desde el inicio (evita "olvidos" de revisión).
- **Localización de fechas y monedas**: `es-CO` en todo el sistema. Confirmar formato de separadores (`.` miles, `,` decimales, típico Colombia).
- **Almacenamiento de archivos**: volumen Docker local vs MinIO. MVP: volumen local. Migración a MinIO si volumen crece.
- **Ajustes contables sobre comparables**: MVP soporta ajuste libre con justificación; validaciones específicas por tipo de ajuste (working capital, one-off) se agregan según se acumulen casos reales.
