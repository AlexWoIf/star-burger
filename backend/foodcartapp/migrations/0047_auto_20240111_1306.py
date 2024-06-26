# Generated by Django 3.2.15 on 2024-01-11 10:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20240111_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время звонка'),
        ),
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время создания'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время доставки'),
        ),
    ]
