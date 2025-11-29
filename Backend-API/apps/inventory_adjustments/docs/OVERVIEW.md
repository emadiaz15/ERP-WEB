# Módulo de Inventario y Ajustes

Replica los procesos legacy de ajustes (`ajustes`, `ajustes_articulos`) e inventarios físicos (`inventarios`, `inventarios_articulos`, `histostock`).

## Entidades
- **StockAdjustment / StockAdjustmentItem**: cabecera y renglones de ajustes manuales.
- **InventoryCount / InventoryCountItem**: planillas de conteo físico con diferencias.
- **StockHistory**: tabla audit trail para cualquier movimiento relevante.

## Endpoints principales (`/api/v1/inventory-adjustments/`)
- `adjustments/` CRUD completo.
- `counts/` CRUD para inventarios.
- `history/` listado paginado y filtrable por producto.

Cada endpoint reutiliza la paginación estándar, invalida cache Redis de 5 minutos y emite eventos websocket mediante `broadcast_crud_event`.
