# Generated by Django 4.2.5 on 2024-03-19 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_attribute_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='attributes',
            field=models.ManyToManyField(blank=True, related_name='products', to='products.attribute'),
        ),
    ]