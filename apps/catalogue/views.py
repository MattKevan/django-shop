from django.views.generic import ListView
from apps.products.models import Product

class ShopView(ListView):
    model = Product
    template_name = 'catalogue/shop.html'
    context_object_name = 'products'
