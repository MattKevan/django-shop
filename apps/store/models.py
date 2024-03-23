from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver   
from django.contrib.auth import get_user_model


class StoreConfiguration(models.Model):
    name = models.CharField(max_length=100, default="My shop")
    description = models.TextField()
    logo = models.ImageField(upload_to='shop/logos/', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and StoreConfiguration.objects.exists():
            raise ValueError("Only one store configuration object can be created.")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Store Configuration"
        verbose_name_plural = "Store Configuration"
    
    
class Shop(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='shop/logos/', null=True, blank=True)
    shop_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner')
    shop_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='members', blank=True)
    slug = models.SlugField(unique=True, blank=True)
  
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            counter = 0
            while Shop.objects.filter(slug=self.slug).exists():
                counter += 1
                self.slug = f"{slugify(self.name)}-{counter}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name