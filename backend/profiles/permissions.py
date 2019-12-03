from rest_framework import permissions

from profiles.models import Membership


class IsTeamOrGroupCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            if request.user == obj.team_creator:
                return True

            return Membership.objects.get(team=obj, user=request.user).is_manager_creator
        except Membership.DoesNotExist:
            return False


class IsTeamOrGroupManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            if request.user == obj.team_creator:
                return True
            member = Membership.objects.get(team=obj, user=request.user)
            return member.is_manager
        except Membership.DoesNotExist:
            return False


class IsTeamOrGroupMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.team_creator:
            return True
        return obj.is_member(request.user)
