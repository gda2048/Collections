from profiles.models import User
from rest_framework import serializers


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'about')
        read_only_fields = ('email', )
