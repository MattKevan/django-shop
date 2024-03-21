from django.urls import path
from . import views
app_name = 'apps.cart'
urlpatterns = [
    path('add/<int:variation_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:variation_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('quantity/<int:variation_id>/', views.update_quantity, name='update_quantity'),
    path('', views.cart_detail, name='cart_detail'),
]