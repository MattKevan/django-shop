from django.shortcuts import render, get_object_or_404
from .models import Product
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from apps.store.models import StoreConfiguration, Shop
from .models import Product, ProductImage
from .forms import ProductCreateForm, ProductImageFormSet, ProductImageForm

def is_store_owner(user):
    return user.groups.filter(name='StoreOwner').exists()

def is_shop_owner(user):
    return user.groups.filter(name='ShopOwner').exists()

def is_shop_owner_or_member(user):
    return user.groups.filter(name__in=['ShopOwner', 'ShopMember']).exists()


def product_page(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variations = product.variations.all()

    for variation in variations:
        variation.parent_options = variation.options.all()
        variation.parent_attributes = [option.attribute for option in variation.parent_options]
        
    return render(request, 'products/product_page.html', {'product': product, 'variations': variations})

@login_required
def create_product(request, shop_slug):
    shop = get_object_or_404(Shop, slug=shop_slug)
    user_shops = Shop.objects.filter(shop_owner=request.user) | Shop.objects.filter(shop_members=request.user)

    # Check if the user is the shop owner or a shop member
    if not (request.user == shop.shop_owner or request.user in shop.shop_members.all()):
        return HttpResponseForbidden("You do not have permission to create products for this shop.")

    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.shop = shop
            product.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('shop_dashboard', shop_slug=shop.slug)
    else:
        form = ProductCreateForm()

    context = {
        'form': form,
        'shop': shop,
        'user_shops': user_shops,

    }
    return render(request, 'products/product-create.html', context)

def is_shop_owner_or_member(user, shop):
    return user == shop.shop_owner or user in shop.shop_members.all()

@login_required
def edit_product(request, shop_slug, product_slug):
    shop = get_object_or_404(Shop, slug=shop_slug)
    product = get_object_or_404(Product, shop=shop, slug=product_slug)

    if not is_shop_owner_or_member(request.user, shop):
        return HttpResponseForbidden("You do not have permission to edit this product.")

    if request.method == 'POST':
        form = ProductCreateForm(request.POST, instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and image_formset.is_valid():
            updated_product = form.save(commit=False)
            updated_product.shop = shop
            updated_product.save()
            image_formset.save()
            return redirect('shop_dashboard_products', shop_slug=shop_slug)
    else:
        form = ProductCreateForm(instance=product)
        image_formset = ProductImageFormSet(instance=product)

    context = {
        'shop': shop,
        'product': product,
        'form': form,
        'image_formset': image_formset,
    }
    return render(request, 'products/product-edit.html', context)

@require_POST
@login_required
def add_product_image(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    image = request.FILES.get('image')
    alt_text = request.POST.get('alt_text')

    if image:
        product_image = ProductImage.objects.create(
            product=product,
            image=image,
            alt_text=alt_text
        )
        return render(request, 'products/product-image.html', {'image': product_image})

    return HttpResponse(status=400)

@require_POST
@login_required
def delete_product_image(request):
    image_id = request.POST.get('image_id')
    image = get_object_or_404(ProductImage, id=image_id)
    image.delete()
    return HttpResponse(status=204)