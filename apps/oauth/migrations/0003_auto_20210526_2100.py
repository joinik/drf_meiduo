# Generated by Django 2.2.5 on 2021-05-26 13:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0002_auto_20210521_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauthqquser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
    ]
