from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from profiles.views import TeamViewSet, confirm_email

team_router = DefaultRouter()
team_router.register(r'', TeamViewSet, basename='teams')


urlpatterns = team_router.urls
