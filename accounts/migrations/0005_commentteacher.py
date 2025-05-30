# Generated by Django 5.1.1 on 2025-03-27 09:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_ratetoteacher_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentTeacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='کامنت')),
                ('create', models.DateTimeField(auto_now_add=True, verbose_name='ساخته شده')),
                ('is_reply', models.BooleanField(default=False, verbose_name='کامنت ریپلای')),
                ('total_comment_report', models.PositiveIntegerField(default=0, verbose_name='تعداد گزارشات')),
                ('comment_report', models.ManyToManyField(blank=True, related_name='com_report', to=settings.AUTH_USER_MODEL, verbose_name='گزارش کامنت')),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_reply', to='accounts.commentteacher', verbose_name='ریپلای')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_comment', to='accounts.teacher', verbose_name='مربی')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_comment', to=settings.AUTH_USER_MODEL, verbose_name='نویسنده')),
            ],
            options={
                'verbose_name': 'کامنت مربی',
                'verbose_name_plural': 'کامنت\u200cهای مربیان',
                'ordering': ['-total_comment_report'],
            },
        ),
    ]
