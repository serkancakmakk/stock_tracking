# Generated by Django 5.0.6 on 2024-06-22 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_bill_number_billitem_discount_1_billitem_discount_2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billitem',
            name='price',
            field=models.DecimalField(decimal_places=3, max_digits=10),
        ),
        migrations.AlterField(
            model_name='billitem',
            name='quantity',
            field=models.DecimalField(decimal_places=3, max_digits=10),
        ),
    ]