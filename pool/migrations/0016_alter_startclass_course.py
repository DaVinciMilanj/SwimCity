# Generated by Django 5.1.1 on 2025-02-27 08:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0015_alter_startclass_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='startclass',
            name='course',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='course', serialize=False, to='pool.classes', verbose_name='دوره'),
        ),
    ]
