# Generated by Django 5.1.1 on 2025-01-09 20:09

import django.core.validators
import django_jalali.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='profile'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='recovery_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='average_rate',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='teacher',
            name='image',
            field=models.ImageField(blank=True, upload_to='teacher'),
        ),
        migrations.AlterField(
            model_name='ratetoteacher',
            name='rate',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='birthday',
            field=django_jalali.db.models.jDateField(),
        ),
        migrations.AddConstraint(
            model_name='ratetoteacher',
            constraint=models.UniqueConstraint(fields=('user', 'teacher'), name='unique_rate_per_user_teacher'),
        ),
    ]
