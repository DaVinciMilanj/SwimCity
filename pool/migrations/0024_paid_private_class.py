# Generated by Django 5.1.1 on 2025-05-20 15:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0023_classes_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='paid',
            name='private_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='paid_private_class', to='pool.privateclass', verbose_name='کلاس خصوصی'),
        ),
    ]
