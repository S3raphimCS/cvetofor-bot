# Generated by Django 5.2.3 on 2025-06-23 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_telegramuser_contact_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramuser',
            name='language_code',
        ),
    ]
