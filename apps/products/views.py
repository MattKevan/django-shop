from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from .models import Shop, Product, ProductImage, Variation
from .forms import ProductCreateForm, ProductImageForm, ProductImageFormSet, VariationFormSet
from django.views.decorators.csrf import csrf_protect

def is_shop_owner_or_member(user, shop):
    return user == shop.shop_owner or user in shop.shop_members.all()

def product_page(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variations = product.variations.all()

    for variation in variations:
        variation.parent_options = variation.options.all()
        variation.parent_attributes = [option.attribute for option in variation.parent_options]
        
    return render(request, 'products/product_page.html', {'product': product, 'variations': variations})

@login_required

@login_required
def add_product(request, shop_slug):
    shop = get_object_or_404(Shop, slug=shop_slug)

    if not is_shop_owner_or_member(request.user, shop):
        return HttpResponseForbidden("You do not have permission to create products for this shop.")

    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        variation_formset = VariationFormSet(request.POST)

        if form.is_valid() and formset.is_valid() and variation_formset.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()

            images = formset.save(commit=False)
            for image in images:
                image.product = product
                image.save()

            variations = variation_formset.save(commit=False)
            for variation in variations:
                variation.product = product
                variation.save()

            return redirect('shop_dashboard_products', shop_slug=shop.slug)
    else:
        form = ProductCreateForm()
        formset = ProductImageFormSet(queryset=ProductImage.objects.none())
        variation_formset = VariationFormSet(queryset=Variation.objects.none())

    context = {
        'shop': shop,
        'form': form,
        'formset': formset,
        'variation_formset': variation_formset,
    }
    return render(request, 'products/product-add.html', context)

@csrf_protect
def edit_product(request, shop_slug, product_slug):
    shop = get_object_or_404(Shop, slug=shop_slug)
    product = get_object_or_404(Product, shop=shop, slug=product_slug)

    if not is_shop_owner_or_member(request.user, shop):
        return HttpResponseForbidden("You do not have permission to edit this product.")

    if request.method == 'POST':
        form = ProductCreateForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        variation_formset = VariationFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid() and variation_formset.is_valid():
            form.save()
            formset.save()
            variation_formset.save()
            return redirect('shop_dashboard_products', shop_slug=shop.slug)
        else:
            # Print form errors
            print("Main form errors:", form.errors)
            print("Image formset errors:", formset.errors)
            print("Variation formset errors:", variation_formset.errors)
    else:
        form = ProductCreateForm(instance=product)
        formset = ProductImageFormSet(instance=product)
        variation_formset = VariationFormSet(instance=product)

    context = {
        'shop': shop,
        'product': product,
        'form': form,
        'formset': formset,
        'variation_formset': variation_formset,
    }
    return render(request, 'products/product-edit.html', context)