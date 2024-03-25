from django.urls import path
from . import views

urlpatterns = [
    path('shop/<slug:slug>/', views.product_page, name='product_page'),
    path('shops/<slug:shop_slug>/products/create/', views.create_product, name='create_product'),
    path('shop/<slug:shop_slug>/products/<slug:product_slug>/edit/', views.edit_product, name='edit_product'),
    path('add-product-image/', views.add_product_image, name='add_product_image'),
    path('delete-product-image/', views.delete_product_image, name='delete_product_image'),
]