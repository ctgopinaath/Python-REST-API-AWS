from django.urls import path
from views import get_all_products, get_product, create_product, update_product, delete_product

urlpatterns = [
    path("products/", get_all_products),
    path("products/<int:product_id>/", get_product),
    path("products/create/", create_product),
    path("products/<int:product_id>/update/", update_product),
    path("products/<int:product_id>/delete/", delete_product),
]
