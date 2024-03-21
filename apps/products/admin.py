from django.contrib import admin
from .models import Product, Collection, Attribute, Option, Variation, ProductTemplate, ProductImage

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0
    fields = ['title']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'attribute':
            kwargs['queryset'] = Attribute.objects.filter(pk=request.resolver_match.kwargs['object_id'])
            kwargs['initial'] = request.resolver_match.kwargs['object_id']
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    search_fields = ['title']
    inlines = [OptionInline]


class VariationInline(admin.TabularInline):
    model = Variation
    fields = ['title', 'price', 'image', 'published']
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [VariationInline, ProductImageInline]

@admin.register(ProductTemplate)
class ProductTemplateAdmin(admin.ModelAdmin):
    autocomplete_fields = ['attributes']
    inlines = [VariationInline]

admin.site.register(ProductImage)
admin.site.register(Collection)
admin.site.register(Variation)