"""Public models for the products app.

This module exposes the main models so they can be imported from
``apps.products.models`` in a compact and explicit way.

Each imported model file contains detailed comments explaining how it
maps to the legacy Visual FoxPro database tables (articulos, rubros,
articulos_clientes, articulos_proveedores, etc.).
"""

from .category_model import Category
from .product_model import Product
from .subproduct_model import Subproduct
from .product_image_model import ProductImage
from .subproduct_image_model import SubproductImage
from .customer_product_model import CustomerProduct
from .supplier_product_model import SupplierProduct
from .supplier_discount_model import SupplierProductDescription, SupplierProductDiscount
from .metrics_model import ProductMetrics
from .dictionary_models import (
	ProductAbbreviation,
	ProductSynonym,
	TermDictionary,
	ProductAlias,
)

__all__ = [
	"Category",
	"Product",
	"Subproduct",
	"ProductImage",
	"SubproductImage",
	"CustomerProduct",
	"SupplierProduct",
	"ProductMetrics",
	"ProductAbbreviation",
	"ProductSynonym",
	"TermDictionary",
	"ProductAlias",
	"SupplierProductDescription",
	"SupplierProductDiscount",
]
