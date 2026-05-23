## Módulo: l10n_mx_edi_addendas_base

**Nombre:** Addendas Extras - Modulo Base
**Versión origen:** 0.1
**Complejidad de migración:** 🟡 Media

### Función
_(sin descripción en manifest)_

### Modelos propios
  - `inherit: res.company`
  - `inherit: product.template`
  - `inherit: product.product`
  - `inherit: sale.order`
  - `inherit: sale.order.line`
  - `inherit: stock.picking`
  - `inherit: account.move`

### Dependencias
  - `account`
  - `product`
  - `sale`
  - `stock`

### Estado
- [ ] pendiente / [ ] en proceso / [x] **migrado — pendiente validación en instancia v19**

### Breaking changes confirmados
- Atributo `attrs=` en XML eliminado en v17 → usar `invisible=`, `readonly=`, `required=` directamente
  - `views\extra_fits_view.xml`

### Notas adicionales
- Módulo base del que dependen 5 addendas. Migrar primero que todas.
- Cambios aquí se propagan a: amece, astra_zeneca, bovedafiscal, coppel, pepsico.
- `attrs=` en `extra_fits_view.xml` — corregir aquí evita repetir en los hijos.

### Decisiones tomadas
_(pendiente)_
