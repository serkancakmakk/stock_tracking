# Generated by Django 5.1 on 2024-08-22 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0106_alter_user_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='set_company_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='tag',
            field=models.CharField(blank=True, choices=[('Kurucu', 'Kurucu'), ('Yönetici', 'Yönetici'), ('Yetkili', 'Yetkili'), ('Destek', 'Destek'), ('Kullanıcı', 'Kullanıcı')], max_length=15, null=True),
        ),
    ]