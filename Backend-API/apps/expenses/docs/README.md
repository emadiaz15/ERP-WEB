# Módulo de Gastos

Este módulo moderniza las tablas legacy asociadas al circuito de gastos y pagos a terceros. El objetivo es exponer un API REST homogénea mientras se preservan las referencias necesarias para una migración progresiva.

## Mapas legacy → modelos Django

| Tabla legacy | Modelo nuevo | Notas clave |
|--------------|--------------|-------------|
| `tiposgastos` | `ExpenseType` | Catálogo administrable de tipos de gasto con `legacy_id` para sincronizar catálogos externos. |
| `gastos` | `Expense` | Cabecera del gasto, con trazabilidad hacia personas (`person_legacy_id`), impuestos y totales segmentados (`net_amount_*`, `vat_amount_*`, percepciones, descuentos y estados). |
| `gastos_articulos` | `ExpenseItem` | Renglones libres asociados a cada gasto (`description`, `quantity`, `unit_amount`, `vat_rate_code`). |
| `gastos_pagos` | `ExpenseDisbursement` | Representa pagos cargados directamente sobre un gasto específico (cheques propios, transferencias puntuales, etc.). |
| `pagosgas` | `ExpensePayment` | Cabecera de un pago masivo/aplicación de fondos contra múltiples gastos. |
| `pagosgas_gastos` | `ExpensePaymentAllocation` | Detalle de imputaciones entre pagos y gastos (monto aplicado, si fue parcial, `legacy_id`). |
| `pagosgas_pagos` | `ExpensePaymentMethod` | Instrumentos de pago utilizados en cada `ExpensePayment` (tipo, banco, cheque, vencimientos). |
| `pagosgas_debintg` | `ExpensePaymentDebitLink` | Relación entre un pago y débitos internos (`debintg`), manteniendo importes y si fue parcial. |

## Endpoints previstos

- `GET/POST /api/v1/expenses/types/` → CRUD de catálogo `ExpenseType`.
- `GET/POST /api/v1/expenses/records/` y `GET/PUT/DELETE /api/v1/expenses/records/<id>/` → Gestión de gastos.
- `POST /api/v1/expenses/records/<id>/approve/` → Workflow de aprobación, registra `approved_at/by` y valida estado.
- `GET/POST /api/v1/expenses/payments/` y `GET/DELETE /api/v1/expenses/payments/<id>/` → Pagos y aplicaciones a gastos.
- `POST /api/v1/expenses/payments/<id>/allocations/` → Imputaciones parciales/totales + retenciones automáticas.

Todos los listados reutilizan la paginación estándar y exponen filtros clave (rango de fechas, tipo, persona, estado) con cache TTL de 5 minutos en ambientes no-`DEBUG`.

## Próximos pasos

1. Afinar reglas de negocio específicas por tipo de gasto (aprobadores múltiples, límites por rol).
2. Preparar scripts de migración desde VFP utilizando los campos `legacy_*` como pivote.
3. Profundizar validaciones y reglas fiscales (retenciones, percepciones automáticas, netos vs. impuestos).
