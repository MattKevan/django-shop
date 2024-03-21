from django.shortcuts import redirect, get_object_or_404, render
from .models import Cart, CartItem
from apps.products.models import Variation
from django.conf import settings
from decimal import Decimal


def add_to_cart(request, variation_id):
    variation = get_object_or_404(Variation, id=variation_id)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    cart_item, created = CartItem.objects.get_or_create(cart=cart, variation=variation)
    if not created:
        cart_item.quantity += quantity  # Add the new quantity to the existing quantity
    else:
        cart_item.quantity = quantity   # Set the quantity for a new cart item
    cart_item.save()

    return redirect('cart:cart_detail')


def remove_from_cart(request, variation_id):
    variation = get_object_or_404(Variation, id=variation_id)
    
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        cart = get_object_or_404(Cart, id=cart_id)

    cart_item = get_object_or_404(CartItem, cart=cart, variation=variation)
    cart_item.delete()


    return redirect('cart:cart_detail')

from django.shortcuts import redirect, get_object_or_404
from .models import CartItem, Variation

def update_quantity(request, variation_id):
    if request.method == 'POST':
        variation = get_object_or_404(Variation, id=variation_id)
        action = request.POST.get('action')

        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            cart_id = request.session.get('cart_id')
            cart = Cart.objects.filter(id=cart_id).first()

        if cart:
            cart_item, created = CartItem.objects.get_or_create(cart=cart, variation=variation)
            if action == 'increment':
                cart_item.quantity += 1
            elif action == 'decrement' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            cart_item.save()

    return redirect('cart:cart_detail')

def cart_detail(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id).first()

    if cart:
        cart_items = cart.items.all()
        subtotal = sum(item.subtotal() for item in cart_items)
        tax_rate = Decimal(settings.TAX_RATE)
        tax = subtotal * tax_rate
        total = subtotal + tax
    else:
        cart_items = []
        subtotal = Decimal('0')
        tax_rate = Decimal(settings.TAX_RATE)
        tax = Decimal('0')
        total = Decimal('0')

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'tax_rate': tax_rate * 100,
    }
    return render(request, 'cart/cart_detail.html', context)