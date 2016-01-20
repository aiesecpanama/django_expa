# coding=utf-8
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from .expaApi import ExpaApi

def get_token(request):
    api = ExpaApi()
    return HttpResponse(api.getToken())

def get_opportunity(request, opID):
    api = ExpaApi()
    return HttpResponse(api.getOpportunity(opID))

class GetOPManagersDataView(TemplateView):
    """Class based view que permite ver los datos de contacto de todos los managers de una oportunidad cuya ID entra como parámetro dentro de la URL"""
    template_name = "yellowPlatform/opmanagers.html"

    def get_context_data(self, **kwargs):
        api = ExpaApi()
        context = super(GetOPManagersDataView, self).get_context_data(**kwargs)
        context["managers"] = api.getOPManagersData(context["opID"])
        return context

class GetAndesYearlyPerformance(TemplateView):
    template_name = "django_expa/monthlyPerformance.html"
    def get_context_data(self, **kwargs):
        api = ExpaApi()
        context = super(GetAndesYearlyPerformance, self).get_context_data(**kwargs)
        context['programs'] = api.getLCYearlyPerformance(2015)
        return context

class GetColombianEBs(TemplateView):
    template_name = "django_expa/contactList.html"
    def get_context_data(self, **kwargs):
        api = ExpaApi()
        context = super(GetColombianEBs, self).get_context_data(**kwargs)
        context['lcs'] = api.getColombiaContactList()
        return context

def test(request, testArg=None):
    api = ExpaApi()
    return HttpResponse(api.test(testArg=testArg))
