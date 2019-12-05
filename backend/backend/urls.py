from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path, re_path
from rest_framework_swagger.views import get_swagger_view

from projects.urls import collections_router, lists_router, items_router

schema_view = get_swagger_view(title='Collections API')

urlpatterns = [
    url(r'^$', schema_view, name='api'),
    re_path(r'teams/', include('profiles.urls')),
    re_path(r'rest-auth/', include('profiles.auth_urls')),
    re_path(r'collections/', include(collections_router.urls)),
    re_path(r'lists/', include(lists_router.urls)),
    re_path(r'items/', include(items_router.urls)),
    path('admin/', admin.site.urls)
]
