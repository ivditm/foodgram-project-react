# Generated by Django 3.2 on 2023-08-10 06:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'default_related_name': 'follow', 'verbose_name': 'подписка', 'verbose_name_plural': 'подписки'},
        ),
    ]
