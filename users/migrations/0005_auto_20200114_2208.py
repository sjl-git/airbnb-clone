# Generated by Django 2.2.5 on 2020-01-14 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200114_2200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='suprehost',
            new_name='superhost',
        ),
    ]