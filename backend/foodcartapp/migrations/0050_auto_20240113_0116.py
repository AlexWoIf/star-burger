# Generated by Django 3.2.15 on 2024-01-12 22:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_order_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='foodcartapp.restaurant', verbose_name='Ресторан'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(blank=True, choices=[('D', 'Наличными при доставке'), ('B', 'Накопленными бонусами/скидками'), ('O', 'Картой онлайн')], db_index=True, default='', max_length=2, verbose_name='Способ оплаты'),
        ),
    ]