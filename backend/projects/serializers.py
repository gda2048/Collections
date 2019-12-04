from profiles.models import Team
from projects.models import Item, List, Collection, Backlog
from rest_framework import serializers
from profiles.serializers import UserDetailsSerializer, TeamSerializer


class ItemSerializer(serializers.ModelSerializer):
    backlog = serializers.PrimaryKeyRelatedField(read_only=True)
    creator = UserDetailsSerializer(read_only=True)
    assigned_user = UserDetailsSerializer(read_only=True)
    list = serializers.PrimaryKeyRelatedField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    last_change = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField()

    class Meta:
        model = Item
        fields = ('pk', 'name', 'description', 'units', 'start_date', 'end_date', 'last_change', 'assigned_user', 'creator',
                  'backlog', 'list')
        read_only_fields = ('start_date', 'last_change', 'assigned_user', 'creator', 'backlog',
                            'list')


class BacklogSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    items = ItemSerializer(many=True)

    class Meta:
        model = Backlog
        fields = ['team', 'items']


class CollectionSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Collection
        fields = ['pk', 'name', 'description', 'date_created', 'lists', 'team']
        read_only_fields = ['date_created', 'lists', 'team']


class ListSerializer(serializers.ModelSerializer):
    collection = serializers.PrimaryKeyRelatedField(read_only=True)
    items = ItemSerializer(many=True)

    class Meta:
        model = List
        fields = ('name', 'collection', 'date_created', 'items')
        read_only_fields = ('collection', 'items', 'date_created')


class TeamCollectionsSerializer(serializers.ModelSerializer):
    """
    Team serializer without linked information about members and groups
    """

    class CollectionSerializer(serializers.ModelSerializer):

        class Meta:
            model = Collection
            fields = ['pk', 'name', 'description', 'date_created', 'lists']
            read_only_fields = ['date_created', 'lists']
    collections = CollectionSerializer(many=True)

    class Meta:
        model = Team
        fields = ('pk', 'team', 'name', 'description', 'is_group', 'date_created', 'collections')
        read_only_fields = ('is_group', 'date_created', 'collections')
