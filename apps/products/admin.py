from django.contrib import admin
from .models import Product, Collection, Attribute, Option, Variation, ProductTemplate


admin.site.register(Collection)
admin.site.register(Variation)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    search_fields = ['title']

admin.site.register(Option)
search_fields = ['name']

class VariationInline(admin.TabularInline):
    model = Variation
    fields = ['title', 'price', 'image']
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['attributes']
    inlines = [VariationInline]

@admin.register(ProductTemplate)
class ProductTemplateAdmin(admin.ModelAdmin):
    autocomplete_fields = ['attributes']
    inlines = [VariationInline]