from profiles.models import User, Team, Membership
from rest_framework import serializers


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'about', 'date_joined')
        read_only_fields = ('email', 'date_joined')


class MemberSerializer(serializers.ModelSerializer):
    user = UserDetailsSerializer(read_only=True)

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
        return UserDetailsSerializer(instance.team_creator).data

    class Meta:
        model = Team
        fields = ('pk', 'team', 'name', 'description', 'members',
                  'groups', 'is_group', 'date_created', 'creator')
        read_only_fields = ('is_group', 'date_created', 'creator')

