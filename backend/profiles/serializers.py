from profiles.models import User, Team
from rest_framework import serializers


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'about')
        read_only_fields = ('email', )


class GroupSerializer(serializers.ModelSerializer):
    """
    Group serializer
    """
    users = UserDetailsSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ('pk', 'is_group', 'name', 'description', 'users')
        read_only_fields = ('date_created',)


class TeamSerializer(serializers.ModelSerializer):
    """
    Team serializer
    """
    users = UserDetailsSerializer(read_only=True)
    team = serializers.PrimaryKeyRelatedField(read_only=True)
    groups = GroupSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ('pk', 'team', 'name', 'description', 'users', 'groups')
        read_only_fields = ('date_created', 'is_group')
