# Generated by Django 5.0.6 on 2024-07-24 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0054_alter_parameter_cost_calculation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='cost_calculation',
            field=models.CharField(choices=[('fifo', 'FIFO'), ('lifo', 'LIFO'), ('average_cost', 'Ortalama Maliyet'), ('specific_identification', 'Belirli Tanımlama'), ('standard_costing', 'Standart Maliyetleme'), ('moving_average', 'Hareketli Ortalama'), ('weighted_average', 'Ağırlıklı Ortalama'), ('replacement_cost', 'Yenileme Maliyeti')], default='fifo', max_length=50),
        ),
    ]
