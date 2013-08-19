from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from questionnaires import views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^questionnaires/', include('questionnaires.urls',
                                     namespace='questionnaires')),
    url(r'^admin/', include(admin.site.urls)),
)
