from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from profiles.models import Team, User


class Backlog(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, primary_key=True, related_name='backlog')

    def __str__(self):
        return self.team.name

    class Meta:
        db_table = 'backlogs'
        verbose_name = 'Backlog'
        verbose_name_plural = 'Backlogs'


@receiver(post_save, sender=Team)
def create_favorites(sender, instance, created, **kwargs):
    if created:
        Backlog.objects.create(team=instance)


class Collection(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1023, blank=True, default='')
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.team.name}:{self.name}'

    class Meta:
        db_table = 'collections'
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        ordering = ['-date_created']


class List(models.Model):
    name = models.CharField(max_length=255)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='lists')
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'lists'
        verbose_name = 'List'
        verbose_name_plural = 'Lists'
        ordering = ['-date_created']


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1023, blank=True, default='')

    start_date = models.DateTimeField('Date created', default=timezone.now)
    last_change = models.DateTimeField('Last change date', auto_now=True)
    end_date = models.DateTimeField('Deadline date', default=timezone.now, null=True)

    units = models.PositiveIntegerField('Number of units', default=0)

    assigned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_items', null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_items')

    backlog = models.ForeignKey(Backlog, on_delete=models.CASCADE, related_name='items')
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='items', null=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.list and self.list.collection.team != self.backlog.team:
            raise ValidationError('Items can be added only from the team backlog')

    class Meta:
        db_table = 'items'
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
