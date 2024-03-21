from django.shortcuts import render, get_object_or_404
from .models import Product

def product_page(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variations = product.variations.all()

    for variation in variations:
        variation.parent_options = variation.options.all()
        variation.parent_attributes = [option.attribute for option in variation.parent_options]
        
    return render(request, 'products/product_page.html', {'product': product, 'variations': variations})