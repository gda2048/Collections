# Generated by Django 2.2.8 on 2020-01-09 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_auto_20200109_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='dosimeter',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='device',
            name='humidity',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='device',
            name='temperature',
            field=models.CharField(max_length=50),
        ),
    ]
