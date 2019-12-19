from rest_framework import serializers

from profiles.models import User, Team, Membership
from projects.models import List, Item


class UserAssignedItemsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'about', 'date_joined')
        read_only_fields = ('email', 'date_joined')


class MemberSerializer(serializers.ModelSerializer):
    user = UserAssignedItemsSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ('user', 'is_manager', 'is_creator', 'date_started')
        read_only_fields = ('is_creator', 'date_started')


class GroupSerializer(serializers.ModelSerializer):
    """
    Group serializer
    """
    members = MemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ('pk', 'name', 'description', 'members', 'is_group', 'date_created')
        read_only_fields = ('is_group', 'date_created')


class TeamSerializer(serializers.ModelSerializer):
    """
    Team serializer
    """
    members = MemberSerializer(many=True, read_only=True)
    team = serializers.PrimaryKeyRelatedField(read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    creator = serializers.SerializerMethodField()

    def get_creator(self, instance):
        return UserAssignedItemsSerializer(instance.team_creator).data

    class Meta:
        model = Team
        fields = ('pk', 'team', 'name', 'description', 'members',
                  'groups', 'is_group', 'date_created', 'creator')
        read_only_fields = ('is_group', 'date_created', 'creator')


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password and with assigned tasks
    """
    """
    TODO rewrite serializer (it is the same as projects.serializer.ItemSerializer)
    """

    class ItemSerializer(serializers.ModelSerializer):
        class ListSerializer(serializers.ModelSerializer):
            class Meta:
                model = List
                fields = ('pk', 'name')
                read_only_fields = ('name',)

        backlog = serializers.PrimaryKeyRelatedField(read_only=True)
        creator = UserAssignedItemsSerializer(read_only=True)
        assigned_user = UserAssignedItemsSerializer(read_only=True)
        list = ListSerializer(read_only=True)
        start_date = serializers.DateTimeField(read_only=True)
        last_change = serializers.DateTimeField(read_only=True)
        end_date = serializers.DateTimeField()

        class Meta:
            model = Item
            fields = ('pk', 'name', 'description', 'units', 'start_date', 'end_date', 'last_change', 'assigned_user',
                      'creator', 'backlog', 'list')
            read_only_fields = ('start_date', 'last_change', 'assigned_user', 'creator', 'backlog',
                                'list')

    assigned_items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'about', 'date_joined', 'assigned_items')
        read_only_fields = ('email', 'date_joined')
