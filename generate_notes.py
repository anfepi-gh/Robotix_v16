"""
Genera MIGRATION_NOTES.md en cada carpeta de addon a partir del
análisis previo. Ejecutar desde la raíz del workspace.
"""
import os, json, subprocess, sys

# ── helpers ──────────────────────────────────────────────────────────────────

def fmt_list(items, indent=2):
    if not items:
        return " _(ninguno)_"
    pad = " " * indent
    return "\n" + "\n".join(f"{pad}- `{i}`" for i in items)

LABEL = {
    "name_get":            "`name_get()` eliminado en v18 → reemplazar por `_compute_display_name()`",
    "old_m2m_tuple":       "Comandos M2M/O2M como tuplas `(0,0,{})` → usar `Command.*()` desde v17",
    "odoo_osv_import":     "`from odoo.osv import` deprecado en v19",
    "record_cr_direct":    "`self._cr / self._uid / self._context` deprecados en v19",
    "inselect_operator":   "Operador de dominio `inselect` eliminado en v18",
    "group_operator_field":"`group_operator=` renombrado a `aggregator=` en v18",
    "check_access_old":    "`check_access_rights/rule()` → `has_access()` / `_filtered_access()` en v18",
    "old_api_decorators":  "Decoradores `@api.multi / @api.one` ya eliminados — revisar compatibilidad",
    "legacy_js_widget":    "JS con `Widget.extend` / `require('web.')` — patrón legacy; migrar a OWL",
    "xml_attrs_string":    "Atributo `attrs=` en XML eliminado en v17 → usar `invisible=`, `readonly=`, `required=` directamente",
    "states_xml_attr":     "Atributo `states=` en XML eliminado en v17 → reemplazar por `invisible=`",
}

COMPLEXITY = {
    # alta
    "ks_dashboard_ninja":                   "Alta",
    "ks_dn_advance":                        "Alta",
    "crm_dashboard":                        "Alta",
    "activity_dashboard_mngmnt":            "Alta",
    "all_in_one_schedule_activity_management": "Alta",
    # media-alta
    "cfdi_complemento_donat":               "Media-Alta",
    "cfdi_complemento_leyendas_fiscales_ee":"Media-Alta",
    "l10n_mx_edi_waybill_extend":           "Media-Alta",
    "l10n_mx_edi_waybill_extend_v40":       "Media-Alta",
    "crm_robotix":                          "Media-Alta",
    # media
    "bi_manual_currency_exchange_rate":     "Media",
    "l10n_mx_edi_addenda_amece":            "Media",
    "l10n_mx_edi_addenda_astra_zeneca":     "Media",
    "l10n_mx_edi_addenda_bovedafiscal":     "Media",
    "l10n_mx_edi_addenda_coppel":           "Media",
    "l10n_mx_edi_addenda_pepsico":          "Media",
    "l10n_mx_edi_addendas_base":            "Media",
    "l10n_mx_edi_40_generic_vat":           "Media",
    "crm_kit":                              "Media",
    "crm_show_all_stages_default":          "Media",
    "rt_activity_mgmt":                     "Media",
    "eti_design_activities":                "Media",
    # baja
    "bi_print_journal_entries":             "Baja",
    "server_action_mass_edit":              "Baja",
    "web_environment_ribbon":               "Baja",
    "eti_mail_activity_extend":             "Baja",
}

EXTRA_NOTES = {
    "eti_design_activities": (
        "- **ALERTA**: versión declarada `13` — este módulo viene de Odoo 13 y funciona en v16 "
        "solo por compatibilidad. Revisar si hay regresiones incluso antes de migrar.\n"
        "- Definiciones de modelos `product.product` y `project.task.type.action` sin `_name` "
        "nuevo — probablemente sobreescriben el core; validar intención."
    ),
    "cfdi_complemento_donat": (
        "- **ALERTA**: versión declarada `15.0.1.0.0` — módulo de Odoo 15 corriendo en v16. "
        "Verificar que funcione correctamente en producción antes de planear migración.\n"
        "- `account.edi.format` fue **eliminado en v17**; toda la lógica EDI se movió al nuevo "
        "framework `l10n_mx_edi` integrado en Odoo core. Requiere reescritura completa del complemento."
    ),
    "cfdi_complemento_leyendas_fiscales_ee": (
        "- **ALERTA**: versión declarada `15.0.1.0.0` — mismo caso que `cfdi_complemento_donat`.\n"
        "- Modelo `complemento.leyenda.fiscal` y `res.partner (Model)` con `_name` igual al core — "
        "revisar si hay conflicto de nombres.\n"
        "- En v17+ el CFDI 4.0 es nativo; evaluar si este complemento sigue siendo necesario "
        "o si Odoo core ya cubre las leyendas fiscales."
    ),
    "l10n_mx_edi_waybill_extend": (
        "- Depende de `l10n_mx_edi_extended` y `l10n_mx_edi_stock` — ambos fueron absorbidos "
        "por `l10n_mx_edi` en v17; las dependencias cambiarán.\n"
        "- Carta Porte versión 3.1 emitida por SAT en 2024 — verificar si la estructura XML "
        "del módulo corresponde a la versión vigente al momento de migrar.\n"
        "- `from odoo.osv import` + `name_get()`: dos breaking changes de distinta versión "
        "(v19 y v18 respectivamente); atacar en orden."
    ),
    "l10n_mx_edi_waybill_extend_v40": (
        "- Depende de `l10n_mx_edi_40` y `l10n_mx_edi_stock_40` — en v17 el CFDI 4.0 "
        "es nativo; estas dependencias desaparecen y debe reapuntarse al core.\n"
        "- Idénticos breaking changes que `l10n_mx_edi_waybill_extend` (`name_get` + `odoo_osv`).\n"
        "- Evaluar fusionar ambos módulos waybill en uno solo para v19."
    ),
    "ks_dashboard_ninja": (
        "- Módulo de tercero (Ksolves). Buscar versión v19 oficial antes de migrar manualmente.\n"
        "- 12 archivos JS con patrón `Widget.extend` — migración completa a OWL requerida "
        "si no hay versión v19 disponible.\n"
        "- `name_get()` detectado en `ks_dashboard_ninja_items.py` — eliminar en v18."
    ),
    "ks_dn_advance": (
        "- Módulo de tercero (Ksolves), extensión de `ks_dashboard_ninja`. "
        "Migrar junto con el módulo base.\n"
        "- TV Dashboard y Website Dashboard tienen JS legacy que puede requerir reescritura total."
    ),
    "crm_dashboard": (
        "- `self._cr` detectado en `models/crm_dashboard.py` — probablemente para SQL directo; "
        "revisar y adaptar al SQL wrapper de v17+.\n"
        "- 2 archivos JS con widgets legacy; evaluar si la funcionalidad puede cubrirse "
        "con las vistas nativas de CRM en v19 antes de reescribir."
    ),
    "crm_robotix": (
        "- Módulo **100% custom** de Robotix — prioridad alta en revisión funcional.\n"
        "- 20 modelos propios / herencias: el de mayor superficie en todo el workspace.\n"
        "- `self._cr` en `crm_lead.py` — verificar si ejecuta SQL raw; adaptar a ORM o "
        "SQL wrapper.\n"
        "- Wizard `move.line.analysis.by.journals` accede a `account.move.line` — "
        "validar compatibilidad con cambios de `account` en v17-v19."
    ),
    "bi_manual_currency_exchange_rate": (
        "- `self._cr / self._uid / self._context` en 3 archivos — patrón frecuente en módulos "
        "de tipo contable; revisar si acceden a cursor directamente para SQL.\n"
        "- Afecta `account.move`, `account.payment` y `sale.order.line` — modelos con cambios "
        "importantes en v17 (nuevos campos de divisa y cálculo de importe).\n"
        "- Verificar compatibilidad con el nuevo motor de pagos de v17+ antes de migrar."
    ),
    "l10n_mx_edi_40_generic_vat": (
        "- Depende de `l10n_mx_edi_40` — módulo que desaparece en v17 (CFDI 4.0 pasa a ser nativo).\n"
        "- Define un modelo `account.move (Model)` con `_name = 'account.move'` — "
        "esto reemplaza el modelo core; confirmar que sea `_inherit` y no una redefinición.\n"
        "- Revisar si la funcionalidad de 'público en general' ya está cubierta nativamente en v19."
    ),
    "rt_activity_mgmt": (
        "- `check_access_rights()` / `check_access_rule()` detectados en `mail_activity.py` — "
        "reemplazar por `has_access()` / `_filtered_access()` en v18.\n"
        "- Evaluar si este módulo y `activity_dashboard_mngmnt` / `all_in_one_schedule_activity_management` "
        "se pueden consolidar en uno; los tres tocan `mail.activity`."
    ),
    "web_environment_ribbon": (
        "- Módulo muy simple; el JS legacy (`ribbon.js`) probablemente ya tiene "
        "versión OWL en la comunidad OCA (`web_environment_ribbon` v17/v18/v19).\n"
        "- Revisar OCA antes de migrar manualmente — probable reemplazo directo."
    ),
    "server_action_mass_edit": (
        "- OCA tiene `server_action_mass_edit` para v16/v17/v18 — buscar versión v19 "
        "antes de migrar manualmente.\n"
        "- `attrs=` en 2 vistas XML — corrección mecánica, baja complejidad."
    ),
    "crm_kit": (
        "- Depende de `crm_dashboard` — migrar juntos y en orden: primero `crm_dashboard`, "
        "luego `crm_kit`.\n"
        "- Módulo de comisiones con modelos propios (`crm.commission`, `commission.wizard`) — "
        "validar que la lógica de comisiones no dependa de APIs de `sale` que cambiaron en v17+."
    ),
    "crm_show_all_stages_default": (
        "- `self._cr` en `crm_lead.py` — probable SQL raw para forzar visibilidad de etapas; "
        "hay formas ORM de lograr esto en v19.\n"
        "- Evaluar si en v19 el CRM ya permite mostrar todas las etapas por configuración "
        "(pipeline stages visibility) antes de mantener código custom."
    ),
    "eti_mail_activity_extend": (
        "- Sin breaking changes detectados en el código.\n"
        "- Versión `0.1` sin número de release Odoo — verificar compatibilidad funcional "
        "con los cambios de `mail.activity` en v17-v19 (el mixin fue reestructurado)."
    ),
    "all_in_one_schedule_activity_management": (
        "- Depende de `sale_management` además de `mail` — revisar si hay lógica que toque "
        "ventas vía actividades; poco frecuente y potencialmente frágil.\n"
        "- Tiene su propio modelo `activity.tag` — igual que `activity_dashboard_mngmnt`. "
        "Evaluar consolidación."
    ),
    "activity_dashboard_mngmnt": (
        "- Duplica modelo `activity.tag` que también existe en `all_in_one_schedule_activity_management`. "
        "Resolver conflicto antes de migrar.\n"
        "- Dashboard JS con librerías legacy (d3, highcharts, Chart.js) en `/lib` — "
        "las librerías en sí no son el problema, sino el wrapper OWL que hay que crear."
    ),
    "l10n_mx_edi_addendas_base": (
        "- Módulo base del que dependen 5 addendas. Migrar primero que todas.\n"
        "- Cambios aquí se propagan a: amece, astra_zeneca, bovedafiscal, coppel, pepsico.\n"
        "- `attrs=` en `extra_fits_view.xml` — corregir aquí evita repetir en los hijos."
    ),
    "l10n_mx_edi_addenda_amece": (
        "- AMECE 7.1. Verificar si el estándar AMECE tiene versión más reciente al momento de migrar.\n"
        "- Modelos propios: `addenda.amece.gln.partner` y `addenda.amece.gtin.product` — "
        "tablas de catálogos que requieren migración de datos."
    ),
    "l10n_mx_edi_addenda_astra_zeneca": (
        "- Addenda específica de cliente. Confirmar con Robotix si este cliente sigue activo "
        "y si la addenda sigue en uso antes de invertir en migración."
    ),
    "l10n_mx_edi_addenda_bovedafiscal": (
        "- Addenda específica de cliente. Misma consideración que AstraZeneca — "
        "confirmar vigencia con Robotix."
    ),
    "l10n_mx_edi_addenda_coppel": (
        "- Toca `account.edi.format` (`inherit: account.edi.format`) — modelo eliminado en v17. "
        "Requiere adaptar la lógica EDI al nuevo framework de v17+.\n"
        "- También extiende `stock.picking` — revisar compatibilidad con cambios de inventario en v17."
    ),
    "l10n_mx_edi_addenda_pepsico": (
        "- Sin modelos propios — solo herencias de `stock.picking`, `sale.order` y `account.move`.\n"
        "- La adición de campos a `account.move` puede interactuar con los cambios de asientos "
        "contables en v17+ (nuevo formato de líneas de impuesto)."
    ),
    "bi_print_journal_entries": (
        "- Sin breaking changes detectados — módulo de solo reporte (QWeb + ir.actions.report).\n"
        "- Revisar que la plantilla QWeb sea compatible con el motor de reportes de v19 "
        "(cambios en `ir.actions.report` y variables de contexto del reporte)."
    ),
}

# ── main ──────────────────────────────────────────────────────────────────────

ADDONS_PATH = r'c:\Desarrollos Locales\Robotix_v16\addons'

# Re-run analysis inline to get fresh data
import ast, re

BREAKING_PATTERNS = {
    'name_get':             r'def\s+name_get\s*\(',
    'old_m2m_tuple':        r'\(\s*[0-4]\s*,\s*0\s*,\s*\{',
    'odoo_osv_import':      r'from\s+odoo\.osv\s+import',
    'record_cr_direct':     r'self\._cr\b|self\._uid\b|self\._context\b',
    'inselect_operator':    r'[\'"]\s*inselect\s*[\'"]',
    'group_operator_field': r'group_operator\s*=',
    'check_access_old':     r'check_access_rights\s*\(|check_access_rule\s*\(',
    'old_api_decorators':   r'@api\.multi|@api\.one|@api\.cr|@api\.v7|@api\.v8',
    'legacy_js_widget':     r'Widget\.extend|require\s*\(\s*["\']web\.',
    'xml_attrs_string':     None,  # handled separately
    'states_xml_attr':      None,  # handled separately
}

results = {}

for mod_name in sorted(os.listdir(ADDONS_PATH)):
    mod_path = os.path.join(ADDONS_PATH, mod_name)
    if not os.path.isdir(mod_path):
        continue
    manifest_path = os.path.join(mod_path, '__manifest__.py')
    if not os.path.exists(manifest_path):
        continue

    with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
        manifest_src = f.read()
    try:
        manifest = ast.literal_eval(manifest_src)
    except Exception:
        manifest = {}

    py_files = []
    for root, dirs, files in os.walk(mod_path):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'static', 'tests']]
        for fname in files:
            if fname.endswith('.py') and fname != '__manifest__.py':
                py_files.append(os.path.join(root, fname))

    models_found, breaking = [], {k: [] for k in BREAKING_PATTERNS}

    for py_path in py_files:
        try:
            with open(py_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        rel = os.path.relpath(py_path, mod_path)
        for m in re.finditer(r'class\s+(\w+)\s*\(.*?models\.(Model|TransientModel|AbstractModel)', content):
            snippet = content[m.start():m.start()+600]
            nm = re.search(r'_name\s*=\s*["\']([^"\']+)["\']', snippet)
            ih = re.search(r'_inherit\s*=\s*["\']([^"\']+)["\']', snippet)
            kind = m.group(2)
            if nm:
                models_found.append(f'{nm.group(1)} ({kind})')
            elif ih:
                models_found.append(f'inherit: {ih.group(1)}')
        for key, pat in BREAKING_PATTERNS.items():
            if pat and re.search(pat, content):
                breaking[key].append(rel)

    js_files = []
    static_src = os.path.join(mod_path, 'static', 'src', 'js')
    if os.path.exists(static_src):
        for root, dirs, files in os.walk(static_src):
            dirs[:] = [d for d in dirs if d != 'lib']
            for fname in files:
                if fname.endswith('.js'):
                    fpath = os.path.join(root, fname)
                    js_files.append(os.path.relpath(fpath, mod_path))
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            jsc = f.read()
                        if re.search(BREAKING_PATTERNS['legacy_js_widget'], jsc):
                            breaking['legacy_js_widget'].append(os.path.relpath(fpath, mod_path))
                    except Exception:
                        pass

    for root, dirs, files in os.walk(mod_path):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'static']]
        for fname in files:
            if fname.endswith('.xml'):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        xc = f.read()
                    rel = os.path.relpath(fpath, mod_path)
                    if re.search(r'attrs\s*=\s*["\']', xc):
                        breaking['xml_attrs_string'].append(rel)
                    if re.search(r'\bstates\s*=\s*["\'][{"]', xc):
                        breaking['states_xml_attr'].append(rel)
                except Exception:
                    pass

    results[mod_name] = {
        'name': manifest.get('name', mod_name),
        'summary': (manifest.get('summary', '') or '').strip()[:200],
        'version': manifest.get('version', '?'),
        'depends': manifest.get('depends', []),
        'models': list(dict.fromkeys(models_found)),
        'breaking': {k: list(dict.fromkeys(v)) for k, v in breaking.items() if v},
        'has_js': bool(js_files),
    }

# ── write files ───────────────────────────────────────────────────────────────

written = []

for mod_name, data in results.items():
    mod_path = os.path.join(ADDONS_PATH, mod_name)
    out_path = os.path.join(mod_path, 'MIGRATION_NOTES.md')

    breaking = data['breaking']
    complexity = COMPLEXITY.get(mod_name, "Media")

    # Breaking changes section
    if breaking:
        bc_lines = []
        for key, files in breaking.items():
            desc = LABEL.get(key, key)
            bc_lines.append(f"- {desc}")
            for f in files[:5]:  # max 5 files per pattern
                bc_lines.append(f"  - `{f}`")
        bc_block = "\n".join(bc_lines)
    else:
        bc_block = "- _(ninguno detectado automáticamente)_"

    # Models section
    if data['models']:
        models_block = "\n".join(f"  - `{m}`" for m in data['models'])
    else:
        models_block = "  - _(ninguno)_"

    # Depends section
    deps_block = "\n".join(f"  - `{d}`" for d in data['depends']) if data['depends'] else "  - _(ninguno)_"

    # Extra notes
    extra = EXTRA_NOTES.get(mod_name, "")
    extra_section = f"\n### Notas adicionales\n{extra}\n" if extra else ""

    # Complexity badge
    badge = {"Alta": "🔴 Alta", "Media-Alta": "🟠 Media-Alta", "Media": "🟡 Media", "Baja": "🟢 Baja"}.get(complexity, complexity)

    summary = data['summary'] or "_(sin descripción en manifest)_"

    content = f"""## Módulo: {mod_name}

**Nombre:** {data['name']}
**Versión origen:** {data['version']}
**Complejidad de migración:** {badge}

### Función
{summary}

### Modelos propios
{models_block}

### Dependencias
{deps_block}

### Estado
- [ ] pendiente / [ ] en proceso / [ ] validado

### Breaking changes confirmados
{bc_block}
{extra_section}
### Decisiones tomadas
_(pendiente)_
"""

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    written.append(mod_name)
    print(f"  OK  {mod_name}")

print(f"\nTotal: {len(written)} archivos MIGRATION_NOTES.md creados.")
