# Generated by Django 5.0.6 on 2024-06-25 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0015_remove_incomingstock_bill_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocktransactions',
            name='processing_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]