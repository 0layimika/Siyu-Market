# Generated by Django 3.2.25 on 2024-07-02 10:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0035_alter_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(verbose_name=datetime.datetime(2024, 7, 2, 10, 57, 47, 326025, tzinfo=utc)),
        ),
    ]
