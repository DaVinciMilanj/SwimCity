# Generated by Django 5.1.1 on 2024-12-10 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_customuser_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='image',
            field=models.ImageField(blank=True, upload_to='teacher'),
        ),
    ]
