# Generated by Django 5.1.6 on 2025-03-18 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_product_name_wishlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='Product',
        ),
        migrations.AddField(
            model_name='wishlist',
            name='products',
            field=models.ManyToManyField(to='myapp.product'),
        ),
    ]
