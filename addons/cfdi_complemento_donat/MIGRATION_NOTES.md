## Módulo: cfdi_complemento_donat

**Nombre:** Complemento CFDI para Donaciones
**Versión origen:** 15.0.1.0.0
**Complejidad de migración:** 🟠 Media-Alta

### Función
Complementos CFDI

### Modelos propios
  - `inherit: account.edi.format` — **ELIMINADO** (modelo removido en v17)
  - `inherit: account.move`
  - `inherit: res.company`
  - `inherit: res.partner`

### Dependencias
  - `l10n_mx_edi_extended` → **ELIMINADO** (absorbido en `l10n_mx_edi` desde v17)
  - `l10n_mx_edi_40` → **ELIMINADO** (CFDI 4.0 nativo en `l10n_mx_edi` desde v17)

### Estado
- [ ] pendiente / [ ] en proceso / [x] **migrado — pendiente validación en instancia v19**

### Breaking changes confirmados
- `account.edi.format` eliminado en v17 — clase `AccountEdiFormat` completa removida
- `l10n_mx_edi_extended` y `l10n_mx_edi_40` eliminados de depends
- Versión `15.0.1.0.0` → `19.0.1.0.0`
- Atributo `attrs=` en XML eliminado en v17 → `readonly=` directo
  - `views\account_move_view.xml`
- `create(vals)` + `@api.model` → `@api.model_create_multi` + `create(vals_list)`
  - `models\account_move.py`

### Decisiones tomadas

**Cambios aplicados:**
- Clase `AccountEdiFormat` (`_inherit = 'account.edi.format'`) eliminada completamente — el modelo fue removido en v17. Sustituida por bloque TODO documentado con opciones de reimplementación
- Hardcoded `self.env['ir.ui.view'].browse(3428)` en la clase eliminada — resuelto por eliminación de la clase
- Imports no utilizados eliminados (etree, minidom, parse, parseString, base64, BytesIO, re, logging, etc.)
- `lxml.objectify.fromstring` conservado — utilizado en `_l10n_mx_edi_decode_cfdi()`
- `@api.model_create_multi` + `create(vals_list)` — modifica cada `vals` dict antes del super()
- `attrs="{'readonly':[('state','!=','draft')]}"` → `readonly="state != 'draft'"`
- `res_company.py` y `res_partner.py` — sin breaking changes, solo field definitions con `_inherit` correcto

**Flags de validación en instancia v19:**
- **CRÍTICO:** Verificar si Odoo Enterprise v19 incluye soporte nativo del complemento Donatarias en `l10n_mx_edi`. Si es así, este módulo completo es innecesario
- **CRÍTICO:** Si no hay soporte nativo, reimplementar la lógica de `AccountEdiFormat` (inyección de namespace `xmlns:donat` y nodo `<donat:Leyenda>` en el CFDI XML) usando el framework v17+. Opciones: override de método Python en `account.move` o QWeb template extendiendo el template CFDI de `l10n_mx_edi`
- `_l10n_mx_edi_decode_cfdi()` en `account_move.py` — método definido en `l10n_mx_edi` v16; verificar si persiste en v17+
- Campos `l10n_mx_edi_donat_auth`, `l10n_mx_edi_donat_date`, `l10n_mx_edi_donat_note` en `res.company` — sin breaking changes de ORM, pero validar que los QWeb templates que los consuman existan en v19
