# Generated by Django 5.0.6 on 2024-07-02 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0032_alter_stocktransactions_incoming_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocktransactions',
            name='outgoing_bill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='stock.outgoingbill'),
        ),
    ]
