# Generated by Django 3.2.18 on 2023-04-14 17:17

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'Пользователь с таким email уже есть'}, help_text='Укажите электронную почту', max_length=254, unique=True, verbose_name='Электронная почта'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'Пользователь с таким username уже есть'}, help_text='Укажите никнейм', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator], verbose_name='Никнейм пользователя'),
        ),
    ]
