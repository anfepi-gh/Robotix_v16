## Módulo: l10n_mx_edi_addenda_astra_zeneca

**Nombre:** Addenda AstraZeneca
**Versión origen:** 0.1
**Complejidad de migración:** 🟡 Media

### Función
Addenda AstraZeneca

### Modelos propios
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
- Addenda específica de cliente. Confirmar con Robotix si este cliente sigue activo y si la addenda sigue en uso antes de invertir en migración.

### Decisiones tomadas

**Cambios aplicados:**
- Eliminados ~15 imports sin usar (zeep, lxml, requests, logging, etc.)
- Clase `ResCompany` renombrada a `ResPartner` (`_inherit = 'res.partner'`)
- `create(vals)` → `@api.model_create_multi` + `create(vals_list)` con `sale_id[0]` para evitar error en multi-registro
- 2 `attrs=` → `invisible=` en `addenda_fields.xml`
- `attrs="{'column_invisible': ...}"` → `column_invisible=` directo (sintaxis v17+)
- Versión → `19.0.1.0.0`

**Flag crítico — requiere validación en v19:**
- `addenda_astra_zeneca.xml` hereda `l10n_mx_edi_40.cfdiv40` — ese template pertenece al módulo `l10n_mx_edi_40` que fue absorbido en v17. En v17+, la generación del XML CFDI ocurre por Python, no por QWeb. El bloque que inyecta `NoIdentificacion` en `cfdi:Concepto` probablemente necesita reimplementarse como override de método Python en `l10n_mx_edi` en lugar de herencia de template.
