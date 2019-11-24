from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    about = models.CharField('О себе', max_length=1023, null=True, blank=True, default='')

    class Meta:
        db_table = 'User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey("self", on_delete=models.CASCADE, related_name='groups', null=True, blank=True)
    is_group = models.BooleanField('Is team?', default=True)
    name = models.CharField('Team name', max_length=255,
                            help_text='Team name max_length=255')
    description = models.CharField('Team description', max_length=1023,
                                   help_text='Team description max_length=1023', null=True, blank=True)
    users = models.ManyToManyField(User, related_name='teams', through='Membership')
    date_created = models.DateTimeField('Date created', default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Member', related_name='memberships')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Team', related_name='members')
    is_manager = models.BooleanField('Is manager?', default=False)
    date_started = models.DateTimeField('Date created', default=timezone.now)

    def __str__(self):
        return f'{self.user}:{self.team}'

    class Meta:
        db_table = 'membership'
        unique_together = ['team', 'user']
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'
