# Generated by Django 5.1.1 on 2025-03-25 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_alter_poolticket_discount_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poolticket',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='ساخته شده'),
        ),
        migrations.AlterField(
            model_name='poolticket',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, verbose_name='تغییر داده شده'),
        ),
    ]
