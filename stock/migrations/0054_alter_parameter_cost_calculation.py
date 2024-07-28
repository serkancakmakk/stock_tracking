# Generated by Django 5.0.6 on 2024-07-24 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0053_alter_parameter_cost_calculation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='cost_calculation',
            field=models.CharField(choices=[('fifo', 'FIFO'), ('lifo', 'LIFO'), ('average_cost', 'Ortalama Maliyet')], default='fifo', max_length=20),
        ),
    ]