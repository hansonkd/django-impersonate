from django.conf.urls.defaults import *


urlpatterns = patterns('impersonate.views',
    url(r'^(?P<uid>\d+)/$',
        'impersonate',
        name='impersonate-start'),
    url(r'^stop/$',
        'stop_impersonate',
        name='impersonate-stop'),
    url(r'^list/$',
        'list_users',
        {'template': 'impersonate/list_users.html'},
        name='impersonate-list'),
    url(r'^search/$',
        'search_users',
        {'template': 'impersonate/search_users.html'},
        name='impersonate-search'),
)
