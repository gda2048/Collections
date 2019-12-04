from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from projects.views import CollectionsViewSet

collections_router = DefaultRouter()
collections_router.register(r'', CollectionsViewSet, base_name='collections')
