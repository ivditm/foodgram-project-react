# Generated by Django 3.2 on 2023-08-10 06:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20230808_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 10, 9, 21, 18, 917381), editable=False, verbose_name='Дата публикации'),
        ),
    ]