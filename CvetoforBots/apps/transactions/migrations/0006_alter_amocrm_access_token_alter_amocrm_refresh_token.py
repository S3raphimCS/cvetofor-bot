# Generated by Django 5.1.4 on 2025-06-26 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_amocrm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amocrm',
            name='access_token',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='amocrm',
            name='refresh_token',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
