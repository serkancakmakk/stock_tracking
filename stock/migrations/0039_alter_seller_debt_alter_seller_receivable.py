# Generated by Django 5.0.6 on 2024-07-17 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0038_alter_seller_debt_alter_seller_receivable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='debt',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='seller',
            name='receivable',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=10, null=True),
        ),
    ]