
from allauth.account.models import EmailConfirmationHMAC
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions

from profiles.models import Team
from serializers import TeamSerializer


def confirm_email(request, key):
    email_confirmation = EmailConfirmationHMAC.from_key(key)
    if email_confirmation:
        email_confirmation.confirm(request)
    return HttpResponseRedirect(reverse_lazy('api'))


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage teams
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.AllowAny]
