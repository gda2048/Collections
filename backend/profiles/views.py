
from allauth.account.models import EmailConfirmationHMAC
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from profiles.exceptions import MemberException
from profiles.models import Team, Membership, User
from serializers import TeamSerializer, GroupSerializer
from profiles.permissions import IsTeamOrGroupCreator, IsTeamOrGroupManager


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

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        team = serializer(data=request.data )
        if team.is_valid():
            obj = Team(**team.validated_data)
            obj.save()
            Membership.objects.create(team=obj, user=request.user, is_manager=True, is_creator=True).save()
            return Response(serializer(obj).data)
        return Response(team.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='add_group', url_name='add_group', serializer_class=GroupSerializer,
            permission_classes=[permissions.IsAuthenticated, IsTeamOrGroupManager])
    def add_group(self, request, pk=None):
        team = self.get_object()
        serializer = self.get_serializer_class()
        group = serializer(data=request.data)
        if team.is_group:
            return Response(data={'errors': ['Team is group']}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if group.is_valid():
            obj = Team(**group.validated_data)
            obj.is_group = True
            obj.team = team
            obj.save()
            Membership.objects.create(team=obj, user=request.user, is_manager=True, is_creator=True).save()
            return Response(serializer(obj).data)
        return Response(team.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='add_member/(?P<username>[^/.]+)',
            url_name='add_member', serializer_class=Serializer,
            permission_classes=[permissions.IsAuthenticated, IsTeamOrGroupManager])
    def add_member(self, request, username, pk=None):
        try:
            user = User.objects.get(username=username)
            team = self.get_object()
            if team.can_be_member(user):
                Membership.objects.create(user=user, team=team)
        except User.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except MemberException as e:
            return Response(data={'errors': [str(e)]}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeamSerializer(team).data)

    @action(detail=True, methods=['delete'], url_path='del_member/(?P<username>[^/.]+)',
            url_name='del_member', serializer_class=Serializer,
            permission_classes=[permissions.IsAuthenticated, IsTeamOrGroupManager])
    def del_member(self, request, username, pk=None):
        try:
            user = User.objects.get(username=username)
            team = self.get_object()
            membership = Membership.objects.get(user=user, team=team)
            if request.user.can_manage_team_member(team, user):
                membership.delete()
            else:
                return Response(data={'errors': ['User can\'t manage this team member']},
                                status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return Response(data={'errors': ['User is not a member of the team']}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeamSerializer(team).data)

    @action(detail=True, methods=['put'], url_path='member_to_manager/(?P<username>[^/.]+)',
            url_name='member_to_manager', serializer_class=Serializer,
            permission_classes=[permissions.IsAuthenticated, IsTeamOrGroupCreator])
    def member_to_manager(self, request, username, pk=None):
        try:
            user = User.objects.get(username=username)
            team = self.get_object()
            membership = Membership.objects.get(user=user, team=team)
            if user == request.user:
                return Response(data={'errors': ['Can\'t edit current user']}, status=status.HTTP_403_FORBIDDEN)
            membership.is_manager = True
            membership.save()
        except User.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return Response(data={'errors': ['User is not a member of the team']}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeamSerializer(team).data)

    @action(detail=True, methods=['put'], url_path='manager_to_member/(?P<username>[^/.]+)',
            url_name='manager_to_member', serializer_class=Serializer,
            permission_classes=[permissions.IsAuthenticated, IsTeamOrGroupCreator])
    def manager_to_member(self, request, username, pk=None):
        try:
            user = User.objects.get(username=username)
            team = self.get_object()
            membership = Membership.objects.get(user=user, team=team)
            if user == request.user:
                return Response(data={'errors': ['Can\'t edit current user']}, status=status.HTTP_403_FORBIDDEN)
            membership.is_manager = False
            membership.save()
        except User.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return Response(data={'errors': ['User is not a member of the team']}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeamSerializer(team).data)