# Generated by Django 2.2.8 on 2020-01-09 18:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_fix_default_is_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.CharField(max_length=10)),
                ('humidity', models.CharField(max_length=10)),
                ('dosimeter', models.CharField(max_length=10)),
                ('message', models.CharField(blank=True, max_length=255)),
                ('result', models.SmallIntegerField(null=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device', to='profiles.Team')),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'db_table': 'device',
            },
        ),
    ]
