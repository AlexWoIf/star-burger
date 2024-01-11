# Generated by Django 3.2.15 on 2024-01-10 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_auto_20240109_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('N', 'NEW'), ('C', 'CHECKING'), ('M', 'MAKING'), ('D', 'DELIVERING'), ('F', 'FINISHED')], db_index=True, default='N', max_length=2, verbose_name='статус'),
        ),
    ]