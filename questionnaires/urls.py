'''
Created on 19.07.2013

@author: dfodorean
'''

from django.conf.urls import patterns, url
from questionnaires import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<questionnaire_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<questionnaire_id>\d+)/results/$',
        views.display_results, name='results_page'),
     url(r'^(?P<questionnaire_id>\d+)/page/(?P<page_id>\d+)/$',
         views.display_page, name='qpage'),
)
