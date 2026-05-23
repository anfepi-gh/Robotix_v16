## Módulo: l10n_mx_edi_addenda_pepsico

**Nombre:** Addenda PepsiCo
**Versión origen:** 1.0
**Complejidad de migración:** 🟡 Media

### Función
Este modulo permite realizar la Addenda PepsiCo.

### Modelos propios
  - `inherit: stock.picking`
  - `inherit: sale.order`
  - `inherit: account.move`

### Dependencias
  - `base`
  - `stock`
  - `sale_stock`
  - `l10n_mx_edi`
  - `l10n_mx_edi_addendas_base`

### Estado
- [ ] pendiente / [ ] en proceso / [x] **migrado — pendiente validación en instancia v19**

### Breaking changes confirmados
- Atributo `attrs=` en XML eliminado en v17 → usar `invisible=`, `readonly=`, `required=` directamente
  - `views\account_invoice.xml`

### Notas adicionales
- Sin modelos propios — solo herencias de `stock.picking`, `sale.order` y `account.move`.
- La adición de campos a `account.move` puede interactuar con los cambios de asientos contables en v17+ (nuevo formato de líneas de impuesto).

### Decisiones tomadas

**Cambios aplicados:**
- Eliminados ~15 imports sin usar (suds, lxml, requests, pytz, base64, etc.)
- `create(vals)` + `@api.model` → `@api.model_create_multi` + `create(vals_list)` con `sale_id[0]`
- 2 `attrs=` → `invisible=` en `account_invoice.xml`
- Versión → `19.0.1.0.0`

**Flags de validación en instancia v19:**
- `l10n_mx_edi_addenda_flag` en `ir.ui.view` — mismo flag que amece/astra_zeneca
- `record.l10n_mx_edi_cfdi_uuid` y `record.l10n_mx_edi_origin` en `addenda_pepsico.xml` — verificar que persisten en v19
