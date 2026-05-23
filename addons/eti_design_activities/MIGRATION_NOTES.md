## Módulo: eti_design_activities

**Nombre:** ETI Design Activities
**Versión origen:** 13 (funcionando en v16 por compatibilidad)
**Complejidad de migración:** 🟡 Media

### Función
Wizard accionable desde `product.product` que genera tareas en el módulo Project. Añade campos `product_id`, `task_type_id` (modelo propio) y `client_id` a `project.task`.

### Modelos propios
  - `design.activities (TransientModel)` — wizard de creación de tareas
  - `project.task.type.action (Model)` — catálogo de tipos de tarea con duración
  - `inherit: project.task` — campos product_id, task_type_id, client_id

### Dependencias
  - `project`

### Estado
- [ ] pendiente / [ ] en proceso / [x] **migrado — pendiente validación en instancia v19**

### Breaking changes confirmados
- `self._context.get(...)` deprecado en v19 → `self.env.context.get(...)`
  - `models\design_activities.py` (default de `product_id`)
- Versión `"13"` → `"19.0.1.0.0"`
- Imports no utilizados eliminados (`_`, `api`) en los tres archivos Python

### Decisiones tomadas

**Cambios aplicados:**
- `self._context.get("active_id")` → `self.env.context.get("active_id")` en lambda default de `product_id`
- Import `_` eliminado de `design_activities.py` y `project_task.py` (no usado)
- Imports `_` y `api` eliminados de `project_task_type_action.py` (sin decoradores ni traducciones)
- Versión `"13"` → `"19.0.1.0.0"` en manifest
- Licencia LGPL-3 — ya correcta, sin cambio

**Nota sobre la alerta del análisis inicial:**
- La nota decía que `product.product` y `project.task.type.action` "probablemente sobreescriben el core" — incorrecto. `project_task.py` usa solo `_inherit = "project.task"` (extensión correcta). `project_task_type_action.py` define un modelo nuevo custom (`_name = "project.task.type.action"`), diferente al nativo `project.task.type` (etapas Kanban). No hay conflicto.

**Flags de validación en instancia v19:**
- `date_assign` en `project.task` — el wizard pasa `"date_assign": datetime.today()` al crear la tarea. En v17+ este campo es computed/stored en el core; escribir en él directamente podría ignorarse o generar error. Verificar si el campo acepta asignación directa en v19 o si debe eliminarse del dict de `create()`.
- `partner_id` en `project.task` — campo nativo en v16; verificar que persiste en v19 (el modelo de Project fue reorganizado en v17).
- Binding `binding_model="product.product"` en `act_window` — probar que el wizard aparece en el menú de Acción dentro de la vista de producto.
