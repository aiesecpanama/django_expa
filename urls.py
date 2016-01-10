# coding=utf-8
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    #url(r'^personas/(?P<pk>\d+)/registrar$', views.registrar, name='registrar'),
    #url(r'^feedback/$', views.feedback, name='feedback'),
    url(r'^token/$', views.get_token, name='get_token'),
    url(r'^opportunity/$', views.get_opportunity, name='get_opportunity'),
    url(r'^test/$', views.test, name='test'),
    url(r'^opportunity/(?P<opID>\d+)/managers$', views.GetOPManagersDataView.as_view(), name='managersOportunidad'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
