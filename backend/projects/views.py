from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from profiles.models import User, Team
from projects.models import Collection, List, Item
from projects.permissions import IsCollectionTeamMember, IsCollectionTeamManager, IsListTeamMember, IsListTeamManager,\
    IsItemTeamCreator, IsItemTeamManager, IsItemTeamMember
from projects.serializers import CollectionSerializer, ListSerializer, CollectionListsSerializer, ItemSerializer


class CollectionsViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
        ViewSet to manage collections
        """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action in ['retrieve', 'lists']:
            permission_classes += [IsCollectionTeamMember]
        if self.action in ['destroy', 'update', 'add_list']:
            permission_classes += [IsCollectionTeamManager]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['post'], url_path='add_list', serializer_class=ListSerializer)
    def add_list(self, request, pk=None):
        try:
            collection = self.get_object()
            list = ListSerializer(data=request.data)
            if list.is_valid():
                list = List(**list.validated_data, collection=collection)
                list.save()
                return Response(ListSerializer(list).data)
            return Response(list.errors, status=status.HTTP_400_BAD_REQUEST)
        except Collection.DoesNotExist:
            return Response(data={'errors': ['Collection is not found']}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='lists', url_name='collections',
            serializer_class=Serializer)
    def lists(self, request, pk=None):
        try:
            collection = self.get_object()
            return Response(CollectionListsSerializer(collection).data)
        except Collection.DoesNotExist:
            return Response(data={'errors': ['Collection is not found']}, status=status.HTTP_404_NOT_FOUND)


class ListViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
        ViewSet to manage lists
        """
    queryset = List.objects.all()
    serializer_class = ListSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action in ['retrieve', 'items']:
            permission_classes += [IsListTeamMember]
        if self.action in ['destroy', 'update', 'add_item']:
            permission_classes += [IsListTeamManager]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['post'], url_path='add_item', url_name='add_item',
            serializer_class=ItemSerializer)
    def add_item(self, request, pk=None):
        try:
            list = self.get_object()
            user = request.user
            item = ItemSerializer(data=request.data)
            if item.is_valid():
                item = Item(**item.validated_data, creator=request.user,
                            backlog=list.collection.team.backlog, list=list)
                item.save()
                return Response(ItemSerializer(item).data)
            return Response(item.errors, status=status.HTTP_400_BAD_REQUEST)
        except List.DoesNotExist:
            return Response(data={'errors': ['List is not found']}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='items', url_name='lists',
            serializer_class=Serializer)
    def items(self, request, pk=None):
        try:
            list = self.get_object()
            return Response(ListSerializer(list).data)
        except List.DoesNotExist:
            return Response(data={'errors': ['List is not found']}, status=status.HTTP_404_NOT_FOUND)


class ItemViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
        ViewSet to manage lists
        """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action in ['retrieve', 'item_to_list']:
            permission_classes += [IsItemTeamMember]
        if self.action in ['destroy', 'update', 'assign_to']:
            permission_classes += [IsItemTeamManager]
        return [permission_class() for permission_class in permission_classes]

    @action(detail=True, methods=['put'], serializer_class=Serializer,
            url_path='assign_to/(?P<username>[^/.]+)', url_name='assign_to')
    def assign_to(self, request, username, pk=None):
        try:
            item = self.get_object()
            user = User.objects.get(username=username)
            team = item.backlog.team
            if team.is_member(user) or user == team.team_creator:
                item.assigned_user = user
                item.save()
                return Response(ItemSerializer(item).data)
            return Response(data={'errors': ['User is not from the team. Task can\'t be assigned to user']},
                            status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response(data={'errors': ['User is not found']}, status=status.HTTP_404_NOT_FOUND)
        except Item.DoesNotExist:
            return Response(data={'errors': ['Item is not found']}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, serializer_class=Serializer, methods=['put'],
            url_path='item_to_team/(?P<team_id>[^/.]+)', url_name='item_to_team')
    def item_to_team(self, request, team_id, pk=None):
        try:
            item = self.get_object()
            to_team = Team.objects.get(id=int(team_id))
            if item.backlog.team.team_creator == to_team.team_creator == request.user:
                if item.backlog != to_team.backlog:
                    item.list = None
                item.backlog = to_team.backlog
                item.save()
                return Response(ItemSerializer(item).data)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Team.DoesNotExist:
            return Response(data={'errors': ['Team is not found']}, status=status.HTTP_404_NOT_FOUND)\


    @action(detail=True, serializer_class=Serializer, methods=['put'],
            url_path='item_to_list/(?P<list_id>[^/.]+)', url_name='item_to_list')
    def item_to_list(self, request, list_id, pk=None):
        try:
            item = self.get_object()
            to_list = List.objects.get(id=int(list_id))
            print(to_list)
            if to_list.collection.team == item.backlog.team:
                item.list = to_list
                item.save()
                return Response(ItemSerializer(item).data)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except List.DoesNotExist:
            return Response(data={'errors': ['List is not found']}, status=status.HTTP_404_NOT_FOUND)