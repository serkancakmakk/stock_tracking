# Generated by Django 5.0.6 on 2024-06-25 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0019_alter_stocktransactions_incoming_bill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocktransactions',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='stock.product'),
        ),
    ]
