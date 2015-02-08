from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'videos.views.categories', name='categories'),
    url(r'^(?P<category>.+?)/$', 'videos.views.videobycategory', name='videos'),
)



