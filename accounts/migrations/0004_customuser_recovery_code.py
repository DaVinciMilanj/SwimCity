# Generated by Django 5.1.1 on 2024-11-18 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_ratetoteacher_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='recovery_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
