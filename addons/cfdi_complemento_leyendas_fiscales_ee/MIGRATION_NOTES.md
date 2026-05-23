## Módulo: cfdi_complemento_leyendas_fiscales_ee

**Nombre:** Complemento - Leyendas Fiscales E.E.
**Versión origen:** 15.0.1.0.0
**Complejidad de migración:** 🟠 Media-Alta

### Función
_(sin descripción en manifest)_

### Modelos propios
  - `inherit: account.move`
  - `complemento.leyenda.fiscal (Model)`
  - `res.partner (Model)`

### Dependencias
  - `l10n_mx_edi_extended`
  - `account`
  - `sale`
  - `l10n_mx_edi`

### Estado
- [ ] pendiente / [ ] en proceso / [x] **migrado — pendiente validación en instancia v19**

### Breaking changes confirmados
- Atributo `attrs=` en XML eliminado en v17 → usar `invisible=`, `readonly=`, `required=` directamente
  - `views\account_invoice_view.xml`
  - `views\res_partner_views.xml`

### Notas adicionales
- **ALERTA**: versión declarada `15.0.1.0.0` — mismo caso que `cfdi_complemento_donat`.
- Modelo `complemento.leyenda.fiscal` y `res.partner (Model)` con `_name` igual al core — revisar si hay conflicto de nombres.
- En v17+ el CFDI 4.0 es nativo; evaluar si este complemento sigue siendo necesario o si Odoo core ya cubre las leyendas fiscales.

### Decisiones tomadas

**Cambios aplicados:**
- `_name = 'res.partner'` eliminado de `res_partner.py` — solo `_inherit` es correcto
- `l10n_mx_edi_extended` eliminado de `depends` — absorbido en `l10n_mx_edi` desde v17
- Comando M2M `(6, 0, ids)` → `Command.set(ids)` en `create()`
- Asignación directa en `_onchange_partner_id` en lugar de `(6, 0, ids)`
- `create(vals)` + `@api.model` → `@api.model_create_multi` + `create(vals_list)` con modificación por elemento antes del super()
- 2 `attrs=` → `invisible=` en `account_invoice_view.xml` y `res_partner_views.xml`
- Versión → `19.0.1.0.0`

**Flags de validación en instancia v19:**
- `_l10n_mx_edi_decode_cfdi()` en `extra_fit.py` — método definido en `l10n_mx_edi` v16; en v17+ la arquitectura EDI cambió completamente. Verificar si el método persiste y si la inyección de `schemaLocation` sigue siendo necesaria o si el core lo maneja.
