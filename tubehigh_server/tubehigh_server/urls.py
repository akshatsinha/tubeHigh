from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tubehigh_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('videos.urls')),
    url(r'^categories/', include('videos.urls')),
    url(r'^category/', include('videos.urls')),
)
