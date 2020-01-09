from allauth.account.models import EmailConfirmationHMAC
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from profiles.exceptions import MemberException
from profiles.models import Team, Membership, User, Device
from profiles.permissions import IsTeamOrGroupCreator, IsTeamOrGroupManager, IsTeamOrGroupMember
from profiles.serializers import TeamSerializer, GroupSerializer, DeviceSerializer
from projects.models import Item, Collection
from projects.serializers import BacklogSerializer, ItemSerializer, CollectionSerializer, TeamCollectionsSerializer


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
        if self.action in ['update', 'destroy', 'member_to_manager', 'manager_to_member']:
            permission_classes += [IsTeamOrGroupCreator]
        if self.action in ['retrieve', 'get_backlog', 'collections', 'add_device']:
            permission_classes += [IsTeamOrGroupMember]
        if self.action in ['add_group', 'del_member', 'add_member', 'add_item', 'add_collection']:
            permission_classes += [IsTeamOrGroupManager]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        team = serializer(data=request.data)
        if team.is_valid():
            obj = Team(**team.validated_data)
            obj.save()
            Membership.objects.create(team=obj, user=request.user, is_manager=True, is_creator=True).save()
            return Response(serializer(obj).data)
        return Response(team.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        List of all teams (not groups) in which current user is found
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer_class()
        queryset = Team.objects.filter(id__in=request.user.memberships.values_list('team__id'), is_group=False)
        page = self.paginate_queryset(queryset)
        if page is not None and request.GET.get('page') is not None:
            chats = serializer(page, many=True)
            return self.get_paginated_response(chats.data)
        chats = serializer(queryset, many=True)
        return Response(chats.data)

    @action(detail=True, methods=['post'], url_path='add_group', url_name='add_group', serializer_class=GroupSerializer)
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

    @action(detail=True, methods=['put'], url_path='add_device', url_name='add_device',
            serializer_class=DeviceSerializer)
    def add_device(self, request, pk=None):
        team = self.get_object()
        serializer = self.get_serializer_class()
        device = serializer(data=request.data)
        if device.is_valid():
            if len(team.device.all()):
                obj = team.device.all()[0]
            else:
                obj = Device()
            obj.team = team
            for key, value in device.validated_data.items():
                setattr(obj, key, value)
            obj.save()
            return Response(serializer(obj).data)
        return Response(device.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='add_member/(?P<username>[^/.]+)',
            url_name='add_member', serializer_class=Serializer)
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
            url_name='del_member', serializer_class=Serializer)
    def del_member(self, request, username, pk=None):
        try:
            user = User.objects.get(username=username)
            team = self.get_object()
            membership = Membership.objects.get(user=user, team=team)
            if request.user.can_manage_team_member(team, user):
                if not team.is_group:
                    for group in team.groups.all():
                        Membership.objects.filter(user=user, team=group).delete()
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
            url_name='member_to_manager', serializer_class=Serializer)
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
            return Response(data={'errors': ['Team is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return Response(data={'errors': ['User is not a member of the team']}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeamSerializer(team).data)

    @action(detail=True, methods=['put'], url_path='manager_to_member/(?P<username>[^/.]+)',
            url_name='manager_to_member', serializer_class=Serializer)
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
            return Response(data={'errors': ['Team is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return Response(data={'errors': ['User is not a member of the team']}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeamSerializer(team).data)

    @action(detail=True, methods=['get'], url_path='backlog', url_name='get_backlog',
            serializer_class=Serializer)
    def get_backlog(self, request, pk=None):
        try:
            team = self.get_object()
            return Response(BacklogSerializer(team.backlog).data)
        except Team.DoesNotExist:
            return Response(data={'errors': ['Team is not found']}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='add_item', url_name='add_item',
            serializer_class=ItemSerializer)
    def add_item(self, request, pk=None):
        try:
            team = self.get_object()
            user = request.user
            item = ItemSerializer(data=request.data)
            if item.is_valid():
                item = Item(**item.validated_data, creator=request.user, backlog=team.backlog)
                item.save()
                return Response(ItemSerializer(item).data)
            return Response(item.errors, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist:
            return Response(data={'errors': ['Team is not found']}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='collections', url_name='collections',
            serializer_class=Serializer)
    def collections(self, request, pk=None):
        try:
            team = self.get_object()
            return Response(TeamCollectionsSerializer(team).data)
        except Team.DoesNotExist:
            return Response(data={'errors': ['Team is not found']}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='add_collection', url_name='add_collection',
            serializer_class=CollectionSerializer)
    def add_collection(self, request, pk=None):
        try:
            team = self.get_object()
            user = request.user
            collection = CollectionSerializer(data=request.data)
            if collection.is_valid():
                collection = Collection(**collection.validated_data, team=team)
                collection.save()
                return Response(CollectionSerializer(collection).data)
            return Response(collection.errors, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist:
            return Response(data={'errors': ['Team is not found']}, status=status.HTTP_404_NOT_FOUND)
