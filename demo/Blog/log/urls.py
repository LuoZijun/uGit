from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from log import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'log.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index ),
    url(r'^add', views.add ),
    url(r'^commit', views.commit ),
    url(r'^blog/(\S+)$', views.articles ),
    url(r'^blog/(\S+)/$', views.category ),
    #url(r'^admin/', include(admin.site.urls)),
)
