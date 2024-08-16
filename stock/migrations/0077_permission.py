# Generated by Django 5.0.6 on 2024-08-09 07:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0076_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_company', models.BooleanField(default=False)),
                ('add_user', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='yetkiler', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
