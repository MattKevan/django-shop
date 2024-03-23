from django.db import models
from django.utils.text import slugify
import itertools
import logging
from django.conf import settings
from datetime import date
from apps.store.models import Shop

# Get an instance of a logger
logger = logging.getLogger(__name__)

def generate_variations(instance):
    if instance.attributes.exists():
        attributes = instance.attributes.all()
        options = [list(attr.options.all()) for attr in attributes]
        option_combinations = list(itertools.product(*options))

        existing_variations = instance.variations.all()
        existing_variation_titles = set(existing_variations.values_list('title', flat=True))

        for combination in option_combinations:
            variation_title = ' - '.join(option.title for option in combination)
            if variation_title not in existing_variation_titles:
                variation = Variation.objects.create(
                    product_template=instance if isinstance(instance, ProductTemplate) else None,
                    product=instance if isinstance(instance, Product) else None,
                    title=variation_title
                )
                variation.options.set(combination)
# Product

class Attribute(models.Model):
    title = models.CharField(max_length=255)
   # options = models.ManyToManyField('Option', related_name='attributes', blank=True)

    def __str__(self):
        return self.title

class Option(models.Model):
    title = models.CharField(max_length=255)
    attribute = models.ForeignKey('Attribute', on_delete=models.CASCADE, related_name='options', null=True)
    def __str__(self):
        return self.title


        
class Variation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='variations', null=True)
    product_template = models.ForeignKey('ProductTemplate', on_delete=models.CASCADE, related_name='variations', null=True)
    title = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='variations/', null=True, blank=True)
    options = models.ManyToManyField(Option, related_name='variations')
    sku = models.CharField(max_length=50, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    published = models.BooleanField(default=True, null=True)
    
    def __str__(self):
        return self.title
    
class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='collections/', blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            counter = 0
            while Collection.objects.filter(slug=self.slug).exists():
                counter += 1
                self.slug = f"{slugify(self.title)}-{counter}"
        super().save(*args, **kwargs)


class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    date_created = models.DateField(default=date.today)  # Converted to DateField
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    collection = models.ManyToManyField('Collection', related_name='products', blank=True)
    attributes = models.ManyToManyField(Attribute, related_name='products', blank=True)
    product_template = models.ForeignKey('ProductTemplate', on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Check if the product template has changed
        template_changed = False
        if self.pk:
            original_product = Product.objects.get(pk=self.pk)
            if original_product.product_template != self.product_template:
                template_changed = True
        else:
            template_changed = True

        super().save(*args, **kwargs)
        logger.debug('Saving product: %s', self.title)


        if template_changed:
            if self.product_template:
                
                logger.debug('Product template is set: %s', self.product_template.title)
                attributes_before = self.attributes.all()
                logger.debug('Current product attributes before setting new ones: %s', list(attributes_before))

                # Delete old variations associated with the product
                self.variations.all().delete()

                # Clear existing attributes from the product
                self.attributes.clear()

                # Add attributes from the product template to the product
                self.attributes.set(self.product_template.attributes.all())

                self.refresh_from_db(fields=['attributes'])
                attributes_after = self.attributes.all()
                logger.debug('New product attributes after setting: %s', list(attributes_after))


                # Generate variations for the product based on the updated attributes
                generate_variations(self)

                # Copy values from template variations to matching product variations
                for template_variation in self.product_template.variations.all():
                    product_variation, created = self.variations.get_or_create(title=template_variation.title)
                    product_variation.price = template_variation.price
                    product_variation.image = template_variation.image
                    product_variation.sku = template_variation.sku
                    product_variation.base_price = template_variation.base_price
                    product_variation.published = template_variation.published
                    product_variation.options.set(template_variation.options.all())
                    product_variation.save()
            else:
                # If no template is selected, delete all variations and clear attributes
                self.variations.all().delete()
                self.attributes.clear()
        else:
            # Update product variations to match the changes made to the template variations
            if self.product_template:
                for template_variation in self.product_template.variations.all():
                    product_variation, created = self.variations.get_or_create(title=template_variation.title)
                    product_variation.price = template_variation.price
                    product_variation.base_price = template_variation.base_price
                    product_variation.sku = template_variation.sku
                    product_variation.image = template_variation.image
                    product_variation.options.set(template_variation.options.all())
                    product_variation.save()

            generate_variations(self)

class ProductImage(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, help_text="A brief description of the image.")

    def __str__(self):
        return f"Image for {self.product.title} ({self.id})"

class ProductTemplate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    attributes = models.ManyToManyField(Attribute, related_name='product_templates', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            counter = 0
            while ProductTemplate.objects.filter(slug=self.slug).exists():
                counter += 1
                self.slug = f"{slugify(self.title)}-{counter}"
        super().save(*args, **kwargs)
        generate_variations(self)
