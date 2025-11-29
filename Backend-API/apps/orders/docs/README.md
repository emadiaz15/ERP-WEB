# Pedidos de clientes

Este módulo centraliza la captura, orquestación y seguimiento del ciclo de pedidos.

Estados del pedido:
- `pending`: pedido creado, esperando gestión.
- `in_process`: asignado / en preparación.
- `completed`: entregado y cerrado.
- `cancelled`: anulado.

Campos clave recientemente agregados:
- `salesperson` y snapshots asociados para conocer el vendedor/viajante responsable.
- `prepared_by`, `prepared_at` para trazar quién preparó el pedido internamente.

Próximos pasos:
- Definir API contracts (creación, edición, seguimiento de estado, asignación de transporte).
- Documentar flujos de integración con Finanzas, Manufactura y Stocks.
- Agregar ejemplos de payloads e invariantes de negocio.
