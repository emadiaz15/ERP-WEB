# Módulo de Clientes

Centraliza la información de clientes legacy (`clientes`, `localidades`, `zonas`, `condiciones impositivas`) y las descripciones de productos asociadas (`articulos_clientes`, `desc_articulos_clientes`).

## Modelos principales
- **Customer**: datos generales, balances legados y referencias a zonas, localidades y condición fiscal.
- **CustomerZone / CustomerLocation / TaxCondition / PostalCode**: catálogos heredados.
- **CustomerProductDetail / CustomerProductDescription**: descripciones personalizadas por cliente y producto.

## Endpoints (`/api/v1/customers/`)
- `customers/` y `customers/<id>/` para CRUD de clientes.
- `product-details/` y `product-details/<id>/` para administrar descripciones personalizadas.

Los listados usan cache Redis de 5 minutos, paginación estándar y emiten eventos websocket para mantener sincronizada la UI.
