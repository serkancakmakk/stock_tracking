# Generated by Django 5.0.6 on 2024-06-24 19:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0013_product_current_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_stock', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('incoming_bill', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='incoming_bills', to='stock.bill')),
                ('outgoing_stock', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='outgoing_stock', to='stock.outgoingstock')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='stock.product')),
            ],
        ),
    ]