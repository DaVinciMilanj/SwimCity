# Generated by Django 5.1.1 on 2025-05-13 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0004_alter_poolticket_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='authority',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='کد پیگیری زرین\u200cپال'),
        ),
    ]
