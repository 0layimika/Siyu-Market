# Generated by Django 3.2.25 on 2024-07-20 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0039_auto_20240720_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='vendor',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Vendor',
        ),
    ]
