# coding=utf-8
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    #url(r'^personas/(?P<pk>\d+)/registrar$', views.registrar, name='registrar'),
    #url(r'^feedback/$', views.feedback, name='feedback'),
    url(r'^token/$', views.get_token, name='get_token'),
    url(r'^ebsColombia/$', views.GetColombianEBs.as_view(), name='colombian_ebs'),
    url(r'^performance/2015$', views.GetAndesYearlyPerformance.as_view(), name='yearly_performance'),
    url(r'^opportunity/(?P<opID>\d+)/$', views.get_opportunity, name='get_opportunity'),
    url(r'^test/$', views.test, name='test'),
    url(r'^test/(?P<testArg>\w+)/$', views.test, name='test2'),
    url(r'^opportunity/(?P<opID>\d+)/managers$', views.GetOPManagersDataView.as_view(), name='managersOportunidad'),

    ]
