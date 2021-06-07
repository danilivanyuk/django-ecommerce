# Generated by Django 3.1 on 2021-05-09 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_auto_20210419_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='gender',
            field=models.CharField(choices=[('man', 'Мужской'), ('women', 'Женский'), ('kid', 'Детский')], default='man', max_length=30, verbose_name='Пол'),
        ),
    ]