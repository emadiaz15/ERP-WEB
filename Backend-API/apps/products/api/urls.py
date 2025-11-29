from django.urls import path
from apps.products.api.views.category_view import category_list, category_detail, create_category
from apps.products.api.views.products_view import product_list, product_detail, create_product
from apps.products.api.views.subproducts_view import subproduct_list, create_subproduct, subproduct_detail
from apps.products.api.views.product_files_view import (
    product_file_upload_view,
    product_file_list_view,
    product_file_delete_view,
    product_file_download_view,
    public_product_file_list_view,
)
from apps.products.api.views.subproduct_files_view import (
    subproduct_file_upload_view,
    subproduct_file_list_view,
    subproduct_file_delete_view,
    subproduct_file_download_view,
    subproduct_file_presign_view,
)
from apps.products.api.views.product_customer_view import (
    product_customer_list_create_view,
    product_customer_detail_view,
)
from apps.products.api.views.product_supplier_view import (
    product_supplier_list_create_view,
    product_supplier_detail_view,
)
from apps.products.api.views.catalog_view import (
    catalog_search_view,
    catalog_product_insight_view,
)
from apps.products.api.views.stock_history_view import product_stock_history_view
from apps.products.api.views.metrics_view import (
    product_metrics_list_view,
    product_metrics_detail_view,
)
from apps.products.api.views.dictionary_view import (
    product_abbreviation_list_view,
    product_abbreviation_detail_view,
    product_synonym_list_view,
    product_synonym_detail_view,
    term_dictionary_list_view,
    term_dictionary_detail_view,
    product_alias_list_view,
    product_alias_detail_view,
)

urlpatterns = [
    # --- 📂 Categorías ---
    path('categories/', category_list, name='category-list'),
    path('categories/create/', create_category, name='category-create'),
    path('categories/<int:category_pk>/', category_detail, name='category-detail'),

    # --- 📦 Productos ---
    path('products/', product_list, name='product-list'),
    path('products/create/', create_product, name='product-create'),
    path('products/<int:prod_pk>/', product_detail, name='product-detail'),

    # --- 🔄 Subproductos ---
    path('products/<int:prod_pk>/subproducts/', subproduct_list, name='subproduct-list'),
    path('products/<int:prod_pk>/subproducts/create/', create_subproduct, name='subproduct-create'),
    path('products/<int:prod_pk>/subproducts/<int:subp_pk>/', subproduct_detail, name='subproduct-detail'),

    # --- 🎞️ Archivos Multimedia de Productos ---
    path('products/<str:product_id>/files/', product_file_list_view, name='product-file-list'),
    path('products/<str:product_id>/files/upload/', product_file_upload_view, name='product-file-upload'),
    path('products/<str:product_id>/files/<path:file_id>/delete/', product_file_delete_view, name='product-file-delete'),
    path('products/<str:product_id>/files/<path:file_id>/download/', product_file_download_view, name='product-file-download'),

    # --- 🌐 Endpoint público ---
    path('public/products/files/', public_product_file_list_view, name='public-product-file-list'),

    # --- 🎞️ Archivos Multimedia de Subproductos ---
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/', subproduct_file_list_view, name='subproduct-file-list'),
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/upload/', subproduct_file_upload_view, name='subproduct-file-upload'),

    # 🔑 usar <path:file_id> porque la key puede incluir "/products/.../subproducts/.../archivo.png"
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/<path:file_id>/delete/', subproduct_file_delete_view, name='subproduct-file-delete'),
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/<path:file_id>/download/', subproduct_file_download_view, name='subproduct-file-download'),

    # ✅ Presign JSON para usar en el frontend (img/video/a)
    path('products/<str:product_id>/subproducts/<str:subproduct_id>/files/<path:file_id>/presign/', subproduct_file_presign_view, name='subproduct-file-presign'),

    # --- 🧾 Configuración por cliente (articulos_clientes) ---
    path('products/<int:prod_pk>/customers/', product_customer_list_create_view, name='product-customer-list-create'),
    path('products/<int:prod_pk>/customers/<int:cp_pk>/', product_customer_detail_view, name='product-customer-detail'),

    # --- 🧾 Configuración por proveedor (articulos_proveedores) ---
    path('products/<int:prod_pk>/suppliers/', product_supplier_list_create_view, name='product-supplier-list-create'),
    path('products/<int:prod_pk>/suppliers/<int:sp_pk>/', product_supplier_detail_view, name='product-supplier-detail'),

    # --- 📚 Catálogo maestro & búsquedas enriquecidas ---
    path('catalog/search/', catalog_search_view, name='catalog-search'),
    path('catalog/products/<int:prod_pk>/insights/', catalog_product_insight_view, name='catalog-product-insight'),
    path('catalog/products/<int:prod_pk>/history/', product_stock_history_view, name='catalog-product-history'),

    # --- 📊 Métricas ---
    path('catalog/metrics/', product_metrics_list_view, name='catalog-metrics-list'),
    path('catalog/products/<int:prod_pk>/metrics/', product_metrics_detail_view, name='catalog-metrics-detail'),

    # --- 📘 Diccionario de términos, abreviaciones y alias ---
    path('catalog/dictionary/abbreviations/', product_abbreviation_list_view, name='catalog-abbreviation-list'),
    path('catalog/dictionary/abbreviations/<int:pk>/', product_abbreviation_detail_view, name='catalog-abbreviation-detail'),
    path('catalog/dictionary/synonyms/', product_synonym_list_view, name='catalog-synonym-list'),
    path('catalog/dictionary/synonyms/<int:pk>/', product_synonym_detail_view, name='catalog-synonym-detail'),
    path('catalog/dictionary/terms/', term_dictionary_list_view, name='catalog-term-list'),
    path('catalog/dictionary/terms/<int:pk>/', term_dictionary_detail_view, name='catalog-term-detail'),
    path('catalog/dictionary/aliases/', product_alias_list_view, name='catalog-alias-list'),
    path('catalog/dictionary/aliases/<int:pk>/', product_alias_detail_view, name='catalog-alias-detail'),
]
