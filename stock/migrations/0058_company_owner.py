# Generated by Django 5.0.6 on 2024-07-27 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0057_company_create_user_alter_company_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='owner',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
