# Generated by Django 5.0.6 on 2024-07-20 21:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0042_alter_seller_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField(max_length=9)),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('other_info', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='bill',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='billitem',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outgoingbill',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outgoingreasons',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='seller',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stocktransactions',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.company'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_issues', models.CharField(choices=[('FIFO', 'FIFO'), ('LIFO', 'LIFO'), ('Average Cost', 'Average Cost')], max_length=20)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock.company')),
            ],
        ),
    ]