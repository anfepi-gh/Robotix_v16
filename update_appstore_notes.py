"""
Actualiza la sección Estado y Decisiones tomadas de los módulos
que serán reemplazados desde OCA o AppStore de terceros.
"""
import os, re

ADDONS = r'c:\Desarrollos Locales\Robotix_v16\addons'

MODULES = {
    # ── OCA (gratuito, GitHub) ────────────────────────────────────────────────
    "web_environment_ribbon": {
        "categoria": "OCA",
        "proveedor": "OCA / web",
        "licencia": "AGPL-3 — libre de usar",
        "url": "https://github.com/OCA/web/tree/19.0",
        "decision": (
            "No migrar manualmente. Obtener versión 19.0 desde el repositorio OCA:\n"
            "`https://github.com/OCA/web/tree/19.0`\n\n"
            "Si OCA no tiene rama 19.0 activa al momento de migrar, usar 18.0 como base."
        ),
    },

    # ── Cybrosys (AppStore LGPL-3, fuente disponible) ────────────────────────
    "activity_dashboard_mngmnt": {
        "categoria": "Cybrosys AppStore",
        "proveedor": "Cybrosys Techno Solutions",
        "licencia": "AGPL-3",
        "url": "https://www.cybrosys.com/odoo/odoo-apps/",
        "decision": (
            "Buscar versión 19.0 en el catálogo de Cybrosys antes de migrar manualmente.\n"
            "Cybrosys publica versiones para cada release de Odoo.\n\n"
            "Nota: Cybrosys tiene TAMBIÉN `all_in_one_schedule_activity_management` con funcionalidad similar. "
            "Evaluar si en v19 se usa uno solo de los dos módulos de actividades de Cybrosys."
        ),
    },
    "all_in_one_schedule_activity_management": {
        "categoria": "Cybrosys AppStore",
        "proveedor": "Cybrosys Techno Solutions",
        "licencia": "LGPL-3",
        "url": "https://www.cybrosys.com/odoo/odoo-apps/",
        "decision": (
            "Buscar versión 19.0 en el catálogo de Cybrosys antes de migrar manualmente.\n\n"
            "Nota: Evaluar consolidación con `activity_dashboard_mngmnt` (mismo proveedor). "
            "En v19 podría bastar con uno de los dos."
        ),
    },
    "crm_dashboard": {
        "categoria": "Cybrosys AppStore",
        "proveedor": "Cybrosys Techno Solutions",
        "licencia": "LGPL-3",
        "url": "https://www.cybrosys.com/odoo/odoo-apps/",
        "decision": (
            "Buscar versión 19.0 en el catálogo de Cybrosys antes de migrar manualmente.\n\n"
            "Dependencia directa: `crm_kit` requiere este módulo — migrar/sustituir primero `crm_dashboard`, luego `crm_kit`."
        ),
    },
    "crm_kit": {
        "categoria": "Cybrosys AppStore",
        "proveedor": "Cybrosys Techno Solutions",
        "licencia": "LGPL-3",
        "url": "https://www.cybrosys.com/odoo/odoo-apps/",
        "decision": (
            "Buscar versión 19.0 en el catálogo de Cybrosys antes de migrar manualmente.\n\n"
            "Depende de `crm_dashboard` — instalar/sustituir en orden: `crm_dashboard` → `crm_kit`."
        ),
    },

    # ── BrowseInfo (AppStore OPL-1, requiere licencia) ───────────────────────
    "bi_manual_currency_exchange_rate": {
        "categoria": "BrowseInfo AppStore",
        "proveedor": "BrowseInfo",
        "licencia": "OPL-1 — requiere compra de licencia v19",
        "url": "https://www.browseinfo.com/odoo-apps",
        "decision": (
            "Verificar disponibilidad de versión 19.0 en el store de BrowseInfo.\n"
            "Si existe, adquirir licencia v19 (OPL-1 no permite reutilizar licencia de v16).\n\n"
            "Alternativa gratuita: buscar en OCA si existe equivalente para `account` en v19 "
            "(`l10n_mx_currency_rate` u otro módulo de tipo de cambio manual)."
        ),
    },
    "bi_print_journal_entries": {
        "categoria": "BrowseInfo AppStore",
        "proveedor": "BrowseInfo",
        "licencia": "OPL-1 — requiere compra de licencia v19",
        "url": "https://www.browseinfo.com/odoo-apps",
        "decision": (
            "Verificar disponibilidad de versión 19.0 en el store de BrowseInfo.\n"
            "Si existe, adquirir licencia v19.\n\n"
            "Alternativa: evaluar si el reporte de asientos de v19 nativo cubre "
            "la necesidad (Odoo mejoró los reportes contables en v17+). "
            "Si es suficiente, descartar este módulo."
        ),
    },

    # ── Ksolves (AppStore OPL-1, requiere licencia) ──────────────────────────
    "ks_dashboard_ninja": {
        "categoria": "Ksolves AppStore",
        "proveedor": "Ksolves India Ltd.",
        "licencia": "OPL-1 — requiere compra de licencia v19",
        "url": "https://store.ksolves.com/",
        "decision": (
            "Verificar disponibilidad de versión 19.0 en store.ksolves.com.\n"
            "Ksolves mantiene Dashboard Ninja activo para cada release de Odoo — alta probabilidad de v19 disponible.\n\n"
            "Si existe, adquirir licencia v19 (no reutilizable desde v16).\n"
            "No migrar manualmente: tiene 12+ archivos JS legacy que requieren reescritura completa en OWL."
        ),
    },
    "ks_dn_advance": {
        "categoria": "Ksolves AppStore",
        "proveedor": "Ksolves India Ltd.",
        "licencia": "OPL-1 — requiere compra de licencia v19",
        "url": "https://store.ksolves.com/",
        "decision": (
            "Mismo tratamiento que `ks_dashboard_ninja` — son un par, se compran y migran juntos.\n"
            "Verificar que la versión v19 de Ksolves incluya el módulo Advance."
        ),
    },

    # ── Relief Technologies (AppStore OPL-1) ─────────────────────────────────
    "rt_activity_mgmt": {
        "categoria": "Relief Technologies AppStore",
        "proveedor": "Relief Technologies",
        "licencia": "OPL-1 — requiere compra de licencia v19",
        "url": "https://apps.odoo.com/apps/modules/browse?author=Relief+Technologies",
        "decision": (
            "Verificar disponibilidad de versión 19.0 en el AppStore de Odoo.\n\n"
            "Alternativa: con `activity_dashboard_mngmnt` y/o `all_in_one_schedule_activity_management` "
            "de Cybrosys (ya en el stack), evaluar si `rt_activity_mgmt` aporta funcionalidad adicional "
            "que no cubren los otros dos. Si hay solapamiento, descartar este módulo en v19."
        ),
    },
}

ESTADO_REEMPLAZO = "- [ ] pendiente / [ ] en proceso / [x] **DECISIÓN TOMADA: obtener versión v19 del proveedor**"
ESTADO_OCA      = "- [ ] pendiente / [ ] en proceso / [x] **DECISIÓN TOMADA: reemplazar desde OCA v19**"

def update_file(mod_name, info):
    path = os.path.join(ADDONS, mod_name, 'MIGRATION_NOTES.md')
    if not os.path.exists(path):
        print(f"  SKIP (no existe): {mod_name}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    estado = ESTADO_OCA if info['categoria'] == 'OCA' else ESTADO_REEMPLAZO

    # Reemplazar bloque Estado
    content = re.sub(
        r'### Estado\n.*?(?=\n###)',
        f'### Estado\n\n{estado}\n',
        content, flags=re.DOTALL
    )

    # Reemplazar bloque Decisiones tomadas
    nuevas_decisiones = (
        f"- **Origen:** {info['proveedor']}\n"
        f"- **Licencia:** {info['licencia']}\n"
        f"- **Referencia:** {info['url']}\n\n"
        f"{info['decision']}"
    )
    content = re.sub(
        r'### Decisiones tomadas\n.*$',
        f'### Decisiones tomadas\n\n{nuevas_decisiones}\n',
        content, flags=re.DOTALL
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  OK  {mod_name}")

for mod, info in MODULES.items():
    update_file(mod, info)

print(f"\nTotal actualizados: {len(MODULES)} módulos.")
