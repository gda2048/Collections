from django.conf.urls import url
from django.urls import include

from profiles.views import confirm_email

urlpatterns = [
    url(r'^', include('rest_auth.urls')),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', confirm_email, name='password_reset_confirm'),
    # after registration user is sent to this url for email confirming
    url(r'^registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        confirm_email,
        name='account_confirm_email'),
    url(r'^registration/account-confirm-email/',
        confirm_email,
        name='account_email_verification_sent'),

    url(r'^registration/', include('rest_auth.registration.urls')),
]