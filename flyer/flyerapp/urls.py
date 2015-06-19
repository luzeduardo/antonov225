__author__ = 'eduardoluz'
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # url( r'^/?$', 'flyerapp.views.index_view', name='home' ),
    url(r'^$', 'flyerapp.views.index'),  # NOQA
	url(r'^add/', 'flyerapp.views.add_schedule', name='add_schedule'),
	url(r'^delete/(?P<index>[0-9]+)', 'flyerapp.views.delete_schedule', name='delete_schedule'),
)