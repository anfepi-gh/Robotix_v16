## Módulo: crm_robotix

**Nombre:** CRM Robotix
**Versión origen:** 16.0.1.0.0
**Complejidad de migración:** 🟠 Media-Alta

### Función
Extensiones 100% custom para el CRM de Robotix: seguimiento de cambios de etapa, reportes de análisis de flujo CRM, análisis de cumplimiento, wizard de salto automático de etapa, catálogos de partners (plan hotel, canal, subcanal, etc.) y reporte de líneas de factura por diario.

### Modelos propios
  - `crm.lead.stages.changes (Model)` — historial de cambios de etapa en oportunidades
  - `crm.stage.next.auto.wizard (TransientModel)` — asigna etapa automática a crm.stage
  - `inherit: res.users` — campo objetivo facturación mensual
  - `inherit: crm.team` — objetivo distribuido por usuarios
  - `inherit: crm.stage` — campos linked_stage_name / linked_stage_id
  - `inherit: crm.lead` — date_won, date_lost, days_won, days_lost, workflow etapas
  - `crm.leads.count.line (Model)` — tabla reporte análisis flujo
  - `crm.leads.count.wizard (TransientModel)` — wizard análisis flujo
  - `crm.leads.won.analisis.line (Model)` — tabla reporte análisis cumplimiento
  - `crm.leads.won.analisis.wizard (TransientModel)` — wizard análisis cumplimiento
  - `partner.plan.hotel (Model)` — catálogo plan hotel
  - `partner.segment.group (Model)` — catálogo grupo partner
  - `partner.financial.branch (Model)` — catálogo unidad financiera
  - `partner.channel.comercial (Model)` — catálogo canal comercial
  - `partner.subchannel.comercial (Model)` — catálogo subcanal
  - `partner.consumption.segment (Model)` — catálogo segmento de consumo
  - `partner.driver.man (Model)` — catálogo choferes
  - `partner.salesman.manager (Model)` — catálogo ejecutivos de ventas
  - `partner.collection.manager (Model)` — catálogo ejecutivos de cobranza
  - `inherit: res.partner` — 10 campos comerciales (plan_hotel_id, driver_id, etc.)
  - `inherit: account.journal` — campo report_invoice_line_access
  - `move.line.analysis.by.journals (Model)` — tabla reporte líneas factura
  - `move.line.analysis.wizard (TransientModel)` — wizard reporte líneas factura (SQL)

### Dependencias
  - `base`
  - `crm`
  - `sale_management`

### Estado
- [ ] pendiente / [ ] en proceso / [x] **migrado — pendiente validación en instancia v19**

### Breaking changes confirmados
- `self._context` deprecado en v19 → `self.env.context`
  - `models/crm_lead.py` (2 ocurrencias: CrmStageNextAutoWizard.execute_report, CRMLead.onchange_stage_linked_new)
- Atributo `attrs=` en XML eliminado en v17 → `readonly=` / `invisible=` directos
  - `views/crm_view.xml` (2 ocurrencias)
- Comando M2M `(6, 0, ids)` → `Command.set(ids)` en v17
  - `wizard/move_line_analysis_by_journals.py` (_get_company_defaults)
- `tracking_msg.field` → `tracking_msg.field_id` en v17+ (`mail.tracking.value` model refactor)
  - `hooks.py` (3 ocurrencias — replace_all aplicado)

### Decisiones tomadas

**Cambios aplicados en Python:**
- `models/crm_lead.py`:
  - Imports eliminados: `calendar`, `date_utils`, `request`, `relativedelta`, `SUPERUSER_ID` (no usados)
  - Imports añadidos: `ast` y `timedelta` (usados en métodos `fix_date()` / `get_name_from_translation()` — muertos pero presentes)
  - 2 × `self._context` → `self.env.context`
- `wizard/move_line_analysis_by_journals.py`:
  - Imports eliminados: `tools`, `SUPERUSER_ID`, `date`, `relativedelta`, `calendar`, `base64`, `xlsxwriter`, `tempfile`, `xl_rowcol_to_cell`, `pytz`, `re`, `math` (todos no usados — generación Excel fue removida en algún momento)
  - Import duplicado `from datetime import datetime, timedelta` eliminado
  - Imports añadidos: `ast`, `Command`
  - `(6, 0, self.env.companies.ids)` → `Command.set(self.env.companies.ids)`
- `hooks.py`:
  - Bug pre-existente corregido: `crm_stage = env['crm.stage']` movido ANTES del loop de mensajes (era `NameError` si lead tenía tracking de etapa)
  - `tracking_msg.field` → `tracking_msg.field_id` (v17+ breaking change en `mail.tracking.value`)

**Cambios en XML:**
- `views/crm_view.xml`:
  - `attrs="{'readonly':[('target_from_users','=',True)]}"` → `readonly="target_from_users"`
  - `attrs="{'invisible':[('linked_stage_id','=',False)]}"` → `invisible="not linked_stage_id"`
- `__manifest__.py`:
  - Versión `16.0.1.0.0` → `19.0.1.0.0`
  - `security/groups_access.xml` añadido al data (antes no estaba — el grupo `access_extra_fits_report_contact` no se creaba en BD)

**Nota sobre `wizard/move_line_analysis_by_journals_view.xml`:**
Este archivo existe pero sigue fuera del manifest intencionalmente. Contiene menús que referencian `account_menu_reports_cava.account_cava_wizard_menu_root` y `account_menu_reports_cava.account_cava_reports_menu_last_requests_root` — IDs externos de un módulo no declarado en `depends`. Cargarlo causaría fallo en install. Pendiente: verificar si `account_menu_reports_cava` existe en el entorno v19 y si es una dependencia real.

**Bug pre-existente detectado (no breaking change):**
- `CRMLeadsWonAnalisisWizard.execute_report()`: el campo Selection tiene `'won_date'` pero el `if` compara contra `'date_won'` — la rama "por fecha de cierre" nunca ejecuta. El reporte siempre filtra por `create_date`. Pre-existing.

### Flags de validación en instancia v19
- `hooks.py` — el `post_init_hook` recorre TODOS los leads y sus mensajes de chatter al instalar. En una BD de producción con muchos leads puede tardar minutos o crashear por timeout. Evaluar si el hook sigue siendo necesario o si ya se ejecutó en v16 y puede desactivarse.
- `tracking_msg.field_id` — verificar que el campo `field_id` en `mail.tracking.value` sea el nombre correcto en v19 (también podría ser `field_info` u otro).
- `wizard/move_line_analysis_by_journals_view.xml` + módulo `account_menu_reports_cava` — resolver la dependencia o eliminar los menús del archivo y añadirlo al manifest.
- `ail.x_studio_unitario_sin_impuestos` en el SQL del wizard — campo creado con Odoo Studio; verificar que exista en la BD v19.
- `res_branch` tabla referenciada en el SQL (`LEFT JOIN res_branch bc ON rp.branch_id = bc.id`) — verificar que el módulo de ramas (multi-company branches) esté instalado en v19.
- `account.journal` inheritance — `account` no está en `depends` explícito; es accesible vía `sale_management` → `account`. Verificar en v19 que la cadena transitiva siga siendo válida.
