# Generated by Django 5.0.6 on 2024-07-31 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0068_remove_product_barcode_1_remove_product_barcode_2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=255, null=True),
        ),
    ]