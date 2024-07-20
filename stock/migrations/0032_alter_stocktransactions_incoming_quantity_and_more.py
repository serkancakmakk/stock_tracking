# Generated by Django 5.0.6 on 2024-07-02 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0031_alter_outgoingbill_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocktransactions',
            name='incoming_quantity',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='stocktransactions',
            name='outgoing_quantity',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
    ]
