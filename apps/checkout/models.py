from django.db import models
from django.conf import settings
import uuid
from apps.products.models import Variation




#
#   ORDERS
#
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"

    def update_total_price(self):
        self.total_price = sum(item.price for item in self.order_items.all())
        self.save()
        
class OrderItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='variations/', null=True, blank=True)
    sku = models.CharField(max_length=50, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_variation = models.ForeignKey(Variation, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.title} - {self.order}"