from django.db import models
from django.utils.text import slugify
import itertools

# Product

class Attribute(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Option(models.Model):
    title = models.CharField(max_length=255)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return self.title	

class Variation(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='variations', null=True)
    product_template = models.ForeignKey('ProductTemplate', on_delete=models.CASCADE, related_name='variations', null=True)
    title = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='variations/', null=True, blank=True)
    options = models.ManyToManyField(Option, related_name='variations')
    
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
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    collection = models.ManyToManyField('Collection', related_name='products', blank=True)
    attributes = models.ManyToManyField(Attribute, related_name='products', blank=True)
    product_template = models.ForeignKey('ProductTemplate', on_delete=models.SET_NULL, related_name='products', null=True, blank=True)

    def __str__(self):
        return self.title

    def generate_variations(self):
        attributes = self.attributes.all()
        options_dict = {}
        for attribute in attributes:
            options_dict[attribute.title] = attribute.options.all()

        variations = []
        if options_dict:
            variations = [dict(zip(options_dict.keys(), v)) for v in itertools.product(*options_dict.values())]

        existing_variations = self.variations.all()
        for variation_data in variations:
            options = []
            title = []
            for attr_title, option in variation_data.items():
                options.append(option)
                title.append(f"{option.title}")

            variation_title = " - ".join(title)

            # Check if a variation with the same options exists for this product
            try:
                variation = self.variations.filter(options__in=options).distinct().get()
            except Variation.DoesNotExist:
                # Create a new variation if it doesn't exist
                variation = Variation.objects.create(product=self, title=variation_title)
                variation.options.set(options)
                variation.save()

        for variation in existing_variations:
            if variation.options.all() not in [list(v.values()) for v in variations]:
                variation.delete()

    def sync_variations(self):
        if self.product_template:
            template_variations = self.product_template.variations.all()
            for template_variation in template_variations:
                options = template_variation.options.all()
                try:
                    variation = self.variations.filter(options__in=options).distinct().get()
                except Variation.DoesNotExist:
                    variation = Variation.objects.create(product=self, title=template_variation.title)
                    variation.options.set(options)
                
                variation.price = template_variation.price
                variation.image = template_variation.image
                variation.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            counter = 0
            while Product.objects.filter(slug=self.slug).exists():
                counter += 1
                self.slug = f"{slugify(self.title)}-{counter}"

        template_changed = False
        if self.pk:
            original_product = Product.objects.get(pk=self.pk)
            if original_product.product_template != self.product_template:
                template_changed = True
        else:
            template_changed = True

        super().save(*args, **kwargs)

        if template_changed:
            if self.product_template:
                self.attributes.set(self.product_template.attributes.all())
                self.sync_variations()
            else:
                self.attributes.clear()
                self.variations.all().delete()
        else:
            self.generate_variations()

class ProductTemplate(models.Model):
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
        self.generate_variations()

    def generate_variations(self):
        attributes = self.attributes.all()
        options_dict = {}
        for attribute in attributes:
            options_dict[attribute.title] = attribute.options.all()

        variations = []
        if options_dict:
            variations = [dict(zip(options_dict.keys(), v)) for v in itertools.product(*options_dict.values())]

        existing_variations = self.variations.all()
        for variation_data in variations:
            title = ' - '.join([f"{key}: {value}" for key, value in variation_data.items()])
            variation, created = Variation.objects.get_or_create(product_template=self, title=title)
            if created:
                for attr_title, option in variation_data.items():
                    attribute = Attribute.objects.get(title=attr_title)
                    variation.options.add(option)
                variation.save()

        for variation in existing_variations:
            if variation.title not in [v['title'] for v in variations]:
                variation.delete()