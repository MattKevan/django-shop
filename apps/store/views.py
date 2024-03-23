from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Q
from django.http import HttpResponseForbidden

from .models import StoreConfiguration, Shop
from apps.products.models import Product


def is_store_owner(user):
    return user.groups.filter(name='StoreOwner').exists()

def is_shop_owner(user):
    return user.groups.filter(name='ShopOwner').exists()

def is_shop_owner_or_member(user):
    return user.groups.filter(name__in=['ShopOwner', 'ShopMember']).exists()

#
#   Store configuration dashboards
#

#   Sore manager dashboard

@user_passes_test(is_store_owner)
def store_manager_dashboard(request):
    store_config = StoreConfiguration.objects.first()
    shops = Shop.objects.all()

    context = {
        'store_config': store_config,
        'shops': shops,
    }
    return render(request, 'store/dashboards/store-manager.html', context)

#   Shop dashboard

def is_shop_owner_or_member(user, shop):
    return user == shop.shop_owner or user in shop.shop_members.all()


@login_required
def shop_dashboard(request, shop_slug):
    shop = get_object_or_404(Shop, slug=shop_slug)

    # Check if the user is the shop owner or a shop member
    if not is_shop_owner_or_member(request.user, shop):
        return HttpResponseForbidden("You do not have permission to access this shop dashboard.")

    # Get the products linked to the shop
    products = Product.objects.filter(shop=shop)

    # Get the other shops the current user is associated with
    user_shops = Shop.objects.filter(shop_owner=request.user) | Shop.objects.filter(shop_members=request.user)
    user_shops = user_shops.exclude(id=shop.id)

    context = {
        'shop': shop,
        'products': products,
        'user_shops': user_shops,
    }
    return render(request, 'store/dashboards/shop-overview.html', context)

@login_required
def shop_dashboard_products(request, shop_slug):
    shop = get_object_or_404(Shop, slug=shop_slug)

    # Check if the user is the shop owner or a shop member
    if not is_shop_owner_or_member(request.user, shop):
        return HttpResponseForbidden("You do not have permission to access this shop dashboard.")

    products = Product.objects.filter(shop=shop)

    # Get the other shops the current user is associated with
    user_shops = Shop.objects.filter(shop_owner=request.user) | Shop.objects.filter(shop_members=request.user)

    context = {
        'shop': shop,
        'products': products,
        'user_shops': user_shops,
    }
    return render(request, 'store/dashboards/shop-products.html', context)

from .forms import ProductCreateForm

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
    return render(request, 'store/dashboards/create-product.html', context)