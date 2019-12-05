from profiles.permissions import IsTeamOrGroupCreator, IsTeamOrGroupManager, IsTeamOrGroupMember


class IsCollectionTeamCreator(IsTeamOrGroupCreator):
    def has_object_permission(self, request, view, obj):
        return IsTeamOrGroupCreator.has_object_permission(self, request, view, obj.team)


class IsCollectionTeamManager(IsTeamOrGroupManager):
    def has_object_permission(self, request, view, obj):
        return IsTeamOrGroupManager.has_object_permission(self, request, view, obj.team)


class IsCollectionTeamMember(IsTeamOrGroupMember):
    def has_object_permission(self, request, view, obj):
        return IsTeamOrGroupMember.has_object_permission(self, request, view, obj.team)


class IsListTeamCreator(IsCollectionTeamCreator):
    def has_object_permission(self, request, view, obj):
        return IsCollectionTeamCreator.has_object_permission(self, request, view, obj.collection)


class IsListTeamManager(IsCollectionTeamManager):
    def has_object_permission(self, request, view, obj):
        return IsCollectionTeamManager.has_object_permission(self, request, view, obj.collection)


class IsListTeamMember(IsCollectionTeamMember):
    def has_object_permission(self, request, view, obj):
        return IsCollectionTeamMember.has_object_permission(self, request, view, obj.collection)


class IsItemTeamMember(IsTeamOrGroupMember):
    def has_object_permission(self, request, view, obj):
        return IsTeamOrGroupMember.has_object_permission(self, request, view, obj.backlog.team)


class IsItemTeamCreator(IsTeamOrGroupCreator):
    def has_object_permission(self, request, view, obj):
        return IsTeamOrGroupCreator.has_object_permission(self, request, view, obj.backlog.team)


class IsItemTeamManager(IsTeamOrGroupManager):
    def has_object_permission(self, request, view, obj):
        return IsTeamOrGroupManager.has_object_permission(self, request, view, obj.backlog.team)
