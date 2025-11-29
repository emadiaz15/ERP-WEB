# Módulo de Ventas

El módulo de ventas replica la estructura ya utilizada en compras para poder incorporar órdenes, remitos y facturas provenientes del ERP legacy.

## Entidades principales
- **SalesOrder**: pedido de venta con referencias al cliente legacy y descuentos.
- **SalesShipment**: remitos/parciales generados desde pedidos.
- **SalesInvoice**: comprobantes fiscales asociados a pedidos y remitos.

Cada entidad posee serializers DRF, repositorios y vistas REST que exponen operaciones CRUD con cacheo de listados (5 minutos) y broadcast de eventos a websockets a través de `broadcast_crud_event`.

## Endpoints
Los endpoints expuestos bajo `/api/v1/sales/` son:
- `orders/` y `orders/<id>/`
- `shipments/` y `shipments/<id>/`
- `invoices/` y `invoices/<id>/`

Todos los endpoints requieren autenticación JWT estándar y heredan la paginación base definida en `apps.core.pagination.Pagination`.
