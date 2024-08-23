# Generated by Django 5.1 on 2024-08-22 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0107_permission_set_company_status_alter_user_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='tag',
            field=models.CharField(blank=True, choices=[('Kurucu', 'Kurucu'), ('Yönetici', 'Yönetici'), ('Yetkili', 'Yetkili'), ('Destek', 'Destek'), ('Kullanıcı', 'Kullanıcı')], default='Kullanıcı', max_length=15, null=True),
        ),
    ]
