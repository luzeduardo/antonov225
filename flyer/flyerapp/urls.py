__author__ = 'eduardoluz'
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # url( r'^/?$', 'flyerapp.views.index_view', name='home' ),
    url(r'^$', 'flyerapp.views.index', name='home'),  # NOQA
    url(r'^edit/', 'flyerapp.views.edit_schedule', name='edit_schedule'),
    url(r'^delete/', 'flyerapp.views.delete_schedule', name='delete_schedule'),
    url(r'^manual/', 'flyerapp.views.manual_exec', name='manual_exec'),
    url(r'^automatic/', 'flyerapp.views.automatic_exec', name='automatic_exec'),
    url(r'^stop-automatic/', 'flyerapp.views.stop_automatic_exec', name='stop_automatic_exec'),
    url(r'^flights/', 'flyerapp.views.flights', name='flights'),
    url(r'^logout/', 'flyerapp.views.logout_view', name='logout'),
)
urlpatterns += staticfiles_urlpatterns()