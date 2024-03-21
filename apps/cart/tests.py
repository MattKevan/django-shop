from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Cart, CartItem
from apps.products.models import Product, Variation
from django.contrib.auth import get_user_model

class CartDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.variation = Variation.objects.create(title='Test Variation', price=10.00)
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, variation=self.variation, quantity=2)

    def test_authenticated_user_with_cart(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart'], self.cart)
        self.assertQuerysetEqual(response.context['cart_items'], [repr(self.cart_item)])
        self.assertEqual(response.context['subtotal'], Decimal('20.00'))
        self.assertEqual(response.context['tax'], Decimal('4.00'))
        self.assertEqual(response.context['total'], Decimal('24.00'))

    def test_authenticated_user_without_cart(self):
        self.user = self.user_model.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='testpass'
        )
        self.client.login(username='testuser2', password='testpass')
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['cart'])
        self.assertQuerysetEqual(response.context['cart_items'], [])
        self.assertEqual(response.context['subtotal'], Decimal('0'))
        self.assertEqual(response.context['tax'], Decimal('0'))
        self.assertEqual(response.context['total'], Decimal('0'))

    def test_unauthenticated_user_with_cart_in_session(self):
        session = self.client.session
        session['cart_id'] = self.cart.id
        session.save()
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart'], self.cart)
        self.assertQuerysetEqual(response.context['cart_items'], [repr(self.cart_item)])
        self.assertEqual(response.context['subtotal'], Decimal('20.00'))
        self.assertEqual(response.context['tax'], Decimal('4.00'))
        self.assertEqual(response.context['total'], Decimal('24.00'))

    def test_unauthenticated_user_without_cart_in_session(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['cart'])
        self.assertQuerysetEqual(response.context['cart_items'], [])
        self.assertEqual(response.context['subtotal'], Decimal('0'))
        self.assertEqual(response.context['tax'], Decimal('0'))
        self.assertEqual(response.context['total'], Decimal('0'))

    def test_calculation_of_subtotal_tax_total(self):
        with self.settings(TAX_RATE=0.2):
            response = self.client.get(reverse('cart:cart_detail'))
            self.assertEqual(response.context['subtotal'], Decimal('20.00'))
            self.assertEqual(response.context['tax'], Decimal('4.00'))
            self.assertEqual(response.context['total'], Decimal('24.00'))