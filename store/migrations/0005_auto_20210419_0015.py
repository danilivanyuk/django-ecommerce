# Generated by Django 3.1 on 2021-04-19 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20210222_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='size',
            field=models.CharField(blank=True, choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], max_length=50, null=True, verbose_name='Размеры'),
        ),
    ]
