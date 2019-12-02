from rest_framework import permissions

from profiles.models import Membership


class IsTeamOrGroupCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return Membership.objects.get(team=obj, user=request.user).is_creator
        except Membership.DoesNotExist:
            return False


class IsTeamOrGroupManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            member = Membership.objects.get(team=obj, user=request.user)
            return member.is_manager or member.is_creator
        except Membership.DoesNotExist:
            return False
