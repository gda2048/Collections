from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from projects.views import CollectionsViewSet, ListViewSet, ItemViewSet

collections_router = DefaultRouter()
collections_router.register(r'', CollectionsViewSet, base_name='collections')

lists_router = DefaultRouter()
lists_router.register(r'', ListViewSet, base_name='lists')

items_router = DefaultRouter()
items_router.register(r'', ItemViewSet, base_name='lists')
