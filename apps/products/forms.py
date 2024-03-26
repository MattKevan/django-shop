from django import forms
from .models import Product, ProductImage, Variation

class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'collection', 'attributes', 'product_template']

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']

ProductImageFormSet = forms.inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=1,
    can_delete=True
)

class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['title', 'image', 'price', 'sku']

VariationFormSet = forms.inlineformset_factory(
    Product,
    Variation,
    form=VariationForm,
    extra=0,
    can_delete=True
)