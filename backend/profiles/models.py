from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from profiles.exceptions import MemberException


class User(AbstractUser):
    about = models.CharField('О себе', max_length=1023, null=True, blank=True, default='')

    def can_manage_team_member(self, team, user):
        if self == team.team_creator:
            return True
        try:
            membership = Membership.objects.get(team=team, user=user)
            self_membership = Membership.objects.get(team=team, user=self)
            if self == user:
                return False
            if self_membership.is_manager and not membership.is_manager:
                return True
            if self_membership.is_creator and membership.is_manager:
                return True
        except Membership.DoesNotExist:
            return False
        return False

    class Meta:
        db_table = 'User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey("self", on_delete=models.CASCADE, related_name='groups', null=True, blank=True)
    is_group = models.BooleanField('Is team?', default=False)
    name = models.CharField('Team name', max_length=255,
                            help_text='Team name max_length=255')
    description = models.CharField('Team description', max_length=1023,
                                   help_text='Team description max_length=1023', null=True, blank=True)
    users = models.ManyToManyField(User, related_name='teams', through='Membership')
    date_created = models.DateTimeField('Date created', default=timezone.now)

    def __str__(self):
        return self.name

    def is_member(self, user: User):
        return self.members.filter(user=user).exists()

    def can_be_member(self, user):
        if self.is_group and not self.team.is_member(user):
            raise MemberException("User is not a member of the team( can't be added to the group)")
        if self.is_member(user):
            raise MemberException("User is already a member of the team")
        if user == self.team_creator:
            return True
        if self.is_group and not self.team.is_member(user):
            raise MemberException("User is not a member of the main team")
        return True

    @property
    def team_creator(self):
        """returns creator of the main team"""
        if self.is_group:
            return Membership.objects.get(team=self.team, is_creator=True).user
        return Membership.objects.get(team=self, is_creator=True).user

    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['-date_created']


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Member', related_name='memberships')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Team', related_name='members')
    is_manager = models.BooleanField('Is manager?', default=False)
    is_creator = models.BooleanField('Is manager?', default=False)
    date_started = models.DateTimeField('Date created', default=timezone.now)

    def __str__(self):
        return f'{self.user}:{self.team}'

    @property
    def is_manager_creator(self):
        return self.is_manager and self.is_creator

    class Meta:
        db_table = 'membership'
        unique_together = ['team', 'user']
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'
        ordering = ['-date_started']


class Device(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='device', unique=True)
    temperature = models.CharField(max_length=50)
    humidity = models.CharField(max_length=50)
    dosimeter = models.CharField(max_length=50)
    message = models.CharField(max_length=255, blank=True)
    result = models.SmallIntegerField(null=True)

    class Meta:
        db_table = 'device'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
