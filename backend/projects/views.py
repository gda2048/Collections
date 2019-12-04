from rest_framework import viewsets, permissions, mixins

from projects.models import Collection
from projects.serializers import CollectionSerializer


class CollectionsViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
        ViewSet to manage teams
        """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.AllowAny]
