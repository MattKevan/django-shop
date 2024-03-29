from django.urls import path
from . import views

urlpatterns = [
    path('shop/<slug:slug>/', views.product_page, name='product_page'),
    path('manage/<slug:shop_slug>/add/', views.add_product, name='add_product'),
    path('manage/<slug:shop_slug>/<slug:product_slug>/edit/', views.edit_product, name='edit_product'),
]