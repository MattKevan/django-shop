from django.urls import path
from . import views

urlpatterns = [
    path('manage/store/', views.store_manager_dashboard, name='store_manager_dashboard'),
    path('manage/<slug:shop_slug>/dashboard', views.shop_dashboard, name='shop_dashboard'),
    path('manage/<slug:shop_slug>/products/', views.shop_dashboard_products, name='shop_dashboard_products'),


    # ...
]