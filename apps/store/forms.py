from django import forms
from apps.products.models import Product

class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'collection', 'attributes', 'product_template']