# Generated by Django 2.2.7 on 2019-11-24 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_add_user_team_membership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='about',
            field=models.CharField(blank=True, default='', max_length=1023, null=True, verbose_name='О себе'),
        ),
    ]
