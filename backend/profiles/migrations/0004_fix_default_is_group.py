# Generated by Django 2.2.7 on 2019-12-01 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_fix_membership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='is_group',
            field=models.BooleanField(default=False, verbose_name='Is team?'),
        ),
    ]
