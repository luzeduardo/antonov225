__author__ = 'eduardoluz'
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # url( r'^/?$', 'flyerapp.views.index_view', name='home' ),
    url(r'^$', 'flyerapp.views.index'),  # NOQA

    url(r'^schedules/$', 'flyerapp.views.schedule_list'),
    url(r'^schedules/(?P<pk>[0-9]+)/$', 'flyerapp.views.schedule_detail'),

    url(r'^add/', 'flyerapp.views.add_schedule', name='add_schedule'),
    url(r'^edit/', 'flyerapp.views.edit_schedule', name='edit_schedule'),
	url(r'^delete/(?P<index>[0-9]+)', 'flyerapp.views.delete_schedule', name='delete_schedule'),
)
urlpatterns += staticfiles_urlpatterns()