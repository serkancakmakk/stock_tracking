# Generated by Django 5.0.6 on 2024-07-10 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0036_delete_parameter_alter_bill_total_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='billitem',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]
