## Módulo: l10n_mx_edi_addenda_amece

**Nombre:** Addenda Amece
**Versión origen:** 0.1
**Complejidad de migración:** 🟡 Media

### Función
Addenda AMECE 7.1

### Modelos propios
  - `addenda.amece.gln.partner (Model)`
  - `addenda.amece.gtin.product (Model)`
  - `inherit: res.company`
  - `inherit: res.partner`
  - `inherit: product.template`
  - `inherit: sale.order`
  - `inherit: account.move`
  - `inherit: sale.order.line`
  - `inherit: account.move.line`

### Dependencias
  - `account`
  - `product`
  - `sale`
  - `stock`
  - `l10n_mx_edi_addendas_base`

### Estado
- [ ] pendiente / [ ] en proceso / [x] **migrado — pendiente validación en instancia v19**

### Breaking changes confirmados
- Atributo `attrs=` en XML eliminado en v17 → usar `invisible=`, `readonly=`, `required=` directamente
  - `views\addenda_fields.xml`

### Notas adicionales
- AMECE 7.1. Verificar si el estándar AMECE tiene versión más reciente al momento de migrar.
- Modelos propios: `addenda.amece.gln.partner` y `addenda.amece.gtin.product` — tablas de catálogos que requieren migración de datos.

### Decisiones tomadas

**Cambios aplicados:**
- Eliminados ~15 imports sin usar (zeep, lxml, requests, logging, base64, etc.)
- Clase `ResCompany` duplicada corregida → renombrada a `ResPartner` para `_inherit = 'res.partner'`
- `create(vals)` → `@api.model_create_multi` + `create(vals_list)` con iteración correcta sobre recordset
- `t-raw` (eliminado en v17) → `t-out` en `addenda_amece.xml` (2 ocurrencias)
- 2 `attrs=` → `invisible=` en `addenda_fields.xml`
- Versión → `19.0.1.0.0`

**Flags de validación en instancia v19 (no se pueden confirmar sin Odoo corriendo):**
- `l10n_mx_edi_addenda_flag` en `ir.ui.view` — campo de `l10n_mx_edi_extended`; verificar si existe en core v19
- `partner.l10n_mx_edi_addenda` — referenciado en `l10n_mx_edi_amece_is_required()`; verificar si persiste en `l10n_mx_edi` v19
- `record._l10n_mx_edi_cfdi_amount_to_text()` — verificar nombre del método en `l10n_mx_edi` v19
- `l10n_mx_edi_cfdi_*` fields en `account.move` — verificar que siguen como computed en v19
- `currency_id.l10n_mx_edi_decimal_places` — verificar que el campo sigue en `l10n_mx_edi` v19
- `l10n_mx_edi_locality` en `res.partner` — verificar que persiste en core v19
- `invoice_repartition_line_ids` / `refund_repartition_line_ids` en tax — verificar nombre en v19
