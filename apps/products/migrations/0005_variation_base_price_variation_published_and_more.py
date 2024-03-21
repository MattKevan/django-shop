# Generated by Django 4.2.5 on 2024-03-20 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='base_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='variation',
            name='published',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AddField(
            model_name='variation',
            name='sku',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
    ]