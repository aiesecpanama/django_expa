# coding=utf-8
"""
Module containing the ExpaApi class
"""
import json
import requests
import urllib

import calendar
from datetime import datetime
from . import tools

#from django_podio.api import PodioApi

class ExpaApi(object):
    """
    This class is meant to encapsulate and facilitate the development of methods that extract information from the GIS API. Whenever a new object of this class is created, it generates a new access token which will be used for all method calls.
    As such tokens expire two hours after being obtained, it is recommended to genetare a new ExpaApi object if your scripts take too long to complete.
    """

    _apiUrl = "https://gis-api.aiesec.org/v1/{palabra1}/{palabra2}?access_token={token}"

    ioDict = {'i': 'opportunity', 'o': 'person'}
    programDict = {'gcdp': 1, 'gip': '2'}

    def __init__(self):
        self.token = requests.post("http://apps.aiesecandes.org/api/token").text

    def _buildQuery(self, routes, queryParams=None, version='v2'):
        """
        Builds a well-formed GIS API query

        version: The version of the API being used. Can be v1 or v2.
        routes: A list of the URI path to the required API REST resource.
        queryParams: A dictionary of query parameters, for GET requests
        """
        if queryParams is None:
            queryParams = {}
        baseUrl = "https://gis-api.aiesec.org/{version}/{routes}?{params}"
        queryParams['access_token'] = self.token
        return baseUrl.format(version=version, routes="/".join(routes), params=urllib.urlencode(queryParams, True))

    def getOpportunity(self, opID):
        """
        Returns the bare JSON data of an opportunity, as obtained from the GIS API.
        """
        response = requests.get(self._buildQuery(['opportunities', opID]))
        return response

    def test(self, **kwargs):
        """
        Test method. Has one kayword argument, 'testArg', to be used when necessary
        """
        print self
        return kwargs['testArg']

    def getManagedEPs(self, expaID):
        """
        Devuelve a todos los EPs que son administrados por el EP manager cuya EXPA ID entra como parámetro
       """
        response = requests.get(self._buildQuery(['people.json'], {'filters[managers][]':[expaID]})).text
        return response

    def getCountryEBs(self, mcID):
        """
        Este método busca dentro de todas las oficinas locales del MC Colombia a los VPs de cada una de ellas para el término 2016
        """
        response = requests.get(self._buildQuery(['committees', '%s.json' % mcID])).text
        lcs = json.loads(response)['suboffices']
        ans = []
        for lc in lcs:
            newLC = {'nombre':lc['full_name']}
            data = self.getLCEBContactList(str(lc['id']))
            newLC['cargos'] = data
            ans.append(newLC)
        return ans

    def getLCEBContactList(self, lcID):
        """
        Este método retorna un diccionario con las personas que conforman la junta ejecutiva del LC cuya ID entra como parámetro, para el periodo 2016
        """
        ans = []
        data = json.loads(requests.get(self._buildQuery(['committees', str(lcID), 'terms.json'])).text)
        for term in data['data']:
            if term['short_name'] == '2016':
                info = requests.get(self._buildQuery(['committees', str(lcID), 'terms', str(term['id']) + '.json'])).text
                info = json.loads(info)
                for team in info['teams']:
                    if team["team_type"] == "eb":
                        for position in team['positions']:
                            person = {}
                            if position['person_id'] is not None:
                                person = tools.getContactData(json.loads(requests.get(self._buildQuery(['people', str(position['person_id']) + '.json'])).text))
                            person['cargo'] = position['position_name']
                            ans.append(person)
                        break
                break
        return ans

    def getOPManagersData(self, opID):
        """
        Éste método devuelve un diccionario con todos los EP Managers y sus datos de contacto de la oportunidad cuya ID entra como parámetro
        """
        #hace un request GET sobre la oportunidad con la ID dada, obtiene el texto, o lo transforma de json a un objeto de python
        opportunity = json.loads(requests.get(self._buildQuery(['opportunities', opID])).text)
        managerData = opportunity["managers"]
        managers = []
        for manager in managerData:
            managers.append(tools.getContactData(manager))
        return managers

    def getMonthStats(self, month, year, program, lc=1395):
        """
        Extrae el ip/ma/re de un mes específico, en un año específico, para un comité y uno de los 4 programas
        """
        queryArgs = {
            'basic[home_office_id]':lc,
            'basic[type]':self.ioDict[program[0]],
            'end_date':'%d-%02d-%02d' % (year, month, calendar.monthrange(year, month)[1]),
            'programmes[]':self.programDict[program[1:]],
            'start_date':'%d-%02d-01' % (year, month)
        }
        query = self._buildQuery(['applications', 'analyze.json'], queryArgs)
        response = json.loads(requests.get(query).text)['analytics']
        return {'MA': response['total_approvals']['doc_count'], 'RE': response['total_realized']['doc_count']}

    def getWeekStats(self, week, year, program, lc=1395):
        """
            Extrae el ip/ma/re de un mes específico, en un año específico, para un comité y uno de los 4 programas


            returns: A dictionary with the following structure:
                {'MA': *number of matches in the given week*,
                 'RE': *# of realizations in the given week*}
        """
        if week == 0:
            weekStart = "%d-01-01" % year
        else:
            weekStart = datetime.strptime('%d %d 1' % (year, week), '%Y %W %w').strftime('%Y-%m-%d')

        weekEnd = datetime.strptime('%d %d 0' % (year, week), '%Y %W %w').strftime('%Y-%m-%d')

        queryArgs = {
            'basic[home_office_id]':lc,
            'basic[type]':self.ioDict[program[0]],
            'end_date':weekEnd,
            'programmes[]':self.programDict[program[1:]],
            'start_date':weekStart
        }
        query = self._buildQuery(['applications', 'analyze.json'], queryArgs)
        response = json.loads(requests.get(query).text)['analytics']
        return {
            'MA': response['total_approvals']['doc_count'],
            'RE': response['total_realized']['doc_count']
            }

    def getLCWeeklyPerformance(self, lc=1395):
        """
        Returns the weekly performance of an LC for a given year, and all four programs

        returns: A dictionary with the following structure:
        {
            'igcdp': *weeklyPerformance for igcdp*,
            ... and so on for all four programs
        }
        """
        answer = {}
        for io in ['i', 'o']:
            for program in ['gcdp', 'gip']:
                answer[io+program] = self.getProgramWeeklyPerformance(io+program, lc)
        return answer

    def getProgramWeeklyPerformance(self, program, office=1395):
        """
        For a given AIESEC office and program, returns its weekly performance, plus its total one during the year. Week 1 starts the first monday of a month.

        Returns: The following dictionary structure:
        {'totals': {
            'MATOTAL': *Total matches in the year*,
            'RETOTAL': *Total realizations in the year*
            },
        'weekly': {
            'MA':[*matches week 0*, *matches week 1*, ...],
            'RE':[*realizations week 0*, *realizations week 1*, ...],
        }
        """
        now = datetime.now()
        currentWeek = int(now.strftime('%W'))
        currentYear = int(now.strftime('%Y'))
        ma = []
        re = []
        maTotal = 0
        reTotal = 0
        for i in range(currentWeek+1):
            weekData = self.getWeekStats(i, currentYear, program, office)
            ma.append(weekData['MA'])
            maTotal += weekData['MA']
            re.append(weekData['RE'])
            reTotal += weekData['RE']
        totals = {'MATOTAL':maTotal, 'RETOTAL':reTotal}
        weekly = {'MA': ma, 'RE': re}
        return {'totals': totals, 'weekly': weekly}

    def getLCYearlyPerformance(self, year, lc=1395):
        """
        Returna el desempeño en matches y realizaciones de un LC en un año dado, separado por mes, para los cuatro programas
        """
        answer = {}
        for io in ['i', 'o']:
            for program in ['gcdp', 'gip']:
                ma = []
                re = []
                for i in range(1, 13):
                    monthData = self.getMonthStats(i, year, io+program, lc)
                    ma.append(monthData['MA'])
                    re.append(monthData['RE'])
                answer[io+program] = {'MA': ma, 'RE': re}
        return answer

#Métodos relacionados con el año actual
    def getCurrentYearStats(self, program, lc=1395):
        """
        Extrae el ma/re de el año actual, para un comité y uno de los 4 programas
        """
        now = datetime.now()
        currentYear = int(now.strftime('%Y'))
        startDate = "%d-01-01" % currentYear

        endDate = now.strftime('%Y-%m-%d')

        queryArgs = {
            'basic[home_office_id]':lc,
            'basic[type]':self.ioDict[program[0]],
            'end_date':endDate,
            'programmes[]':self.programDict[program[1:]],
            'start_date':startDate
        }
        query = self._buildQuery(['applications', 'analyze.json'], queryArgs)
        response = json.loads(requests.get(query).text)['analytics']
        return {
            'MA': response['total_approvals']['doc_count'],
            'RE': response['total_realized']['doc_count']
            }

    def getCountryCurrentYearStats(self, program, lc=1551):
        """
        Extrae el ma/re de el año actual, para un comité y uno de los 4 programas
        """
        now = datetime.now()
        currentYear = int(now.strftime('%Y'))
        startDate = "%d-01-01" % currentYear

        endDate = now.strftime('%Y-%m-%d')

        queryArgs = {
            'basic[home_office_id]':lc,
            'basic[type]':self.ioDict[program[0]],
            'end_date':endDate,
            'programmes[]':self.programDict[program[1:]],
            'start_date':startDate
        }
        query = self._buildQuery(['applications', 'analyze.json'], queryArgs)
        try:
            lcData = json.loads(requests.get(query).text)['analytics']['children']['buckets']
            response = {}
            for lc in lcData:
                response[lc['key']] = {'MA': lc['total_approvals']['doc_count'], 'RE': lc['total_realized']['doc_count']}

        except KeyError as e:
            print e
            print json.loads(requests.get(query).text)
            raise e
        return response

#Listas de MCs, LCs, regiones y similares

    def getRegions(self):
        """
            Gets the information of all AIESEC regions. 1626 is the EXPA id of AIESEC INTERNATIONAL; all regions appear as suboffices
        """
        query = self._buildQuery(['committees', '1626.json'])
        return json.loads(requests.get(query).text)['suboffices']

    def getMCs(self, region):
        """
        Gets the information of all countries inside a given AIESEC region, whose ID enters as a parameter
        """
        query = self._buildQuery(['committees', '%d.json' % region])
        return json.loads(requests.get(query).text)['suboffices']

    def getSuboffices(self, subofficeID):
        """
        Gets the information of all countries inside a given AIESEC region, whose ID enters as a parameter
        """
        query = self._buildQuery(['committees', '%d.json' % subofficeID])
        return json.loads(requests.get(query).text)['suboffices']

####################
############ Analytics sobre people, que permitan obtener personas que cumplen o no cumplen ciertos criterios
####################

    def getUncontactedEPs(self):
        """
        Returns all EPs belonging to the token owner's LC who have not been contacted yet, up to 100. It also returns the total number.
        """
        query = self._buildQuery(['people.json',], {
            'filters[contacted]': 'false',
            'filters[registered[from]]':'2016-01-01',
            'page':1,
            'per_page':100
        })
        data = json.loads(requests.get(query).text)
        totals = {}
        totals['total'] = data['paging']['total_items']
        totals['eps'] = data['data']
        return totals

    def getWeekRegistered(self, week=None, year=None):
        """
        Extrae a las personas, y el número de personas, que se registraron en EXPA desde el lunes anterior. If no week or year arguments are given, uses the current week

        returns: A dictionary with the following structure:
            {'total': *number of people who registered that week*,
             'eps': *the eps who registered*}
        """
        if week == None or year == None:
            now = datetime.now()
            week = int(now.strftime('%W'))
            year = int(now.strftime('%Y'))

        if week == 0:
            weekStart = "%d-01-01" % year
        else:
            weekStart = datetime.strptime('%d %d 1' % (year, week), '%Y %W %w').strftime('%Y-%m-%d')

        weekEnd = datetime.strptime('%d %d 0' % (year, week), '%Y %W %w').strftime('%Y-%m-%d')

        query = self._buildQuery(['people.json',], {
            'filters[registered[from]]':weekStart,
            'filters[registered[to]]':weekEnd,
            'page':1,
            'per_page':100
        })
        data = json.loads(requests.get(query).text)
        totals = {}
        totals['total'] = data['paging']['total_items']
        totals['eps'] = data['data']
        return totals

    def getWeekContacted(self, week=None, year=None):
        """
        Extrae a las personas, y el número de personas, que han sido contactadas en EXPA desde el lunes anterior. If no week or year arguments are given, uses the current week

        returns: A dictionary with the following structure:
            {'total': *number of people who registered that week*,
             'eps': *the eps who registered*}
        """
        if week == None or year == None:
            now = datetime.now()
            week = int(now.strftime('%W'))
            year = int(now.strftime('%Y'))

        if week == 0:
            weekStart = "%d-01-01" % year
        else:
            weekStart = datetime.strptime('%d %d 1' % (year, week), '%Y %W %w').strftime('%Y-%m-%d')

        weekEnd = datetime.strptime('%d %d 0' % (year, week), '%Y %W %w').strftime('%Y-%m-%d')

        query = self._buildQuery(['people.json',], {
            'filters[contacted_at[from]]':weekStart,
            'filters[contacted_at[to]]':weekEnd,
            'page':1,
            'per_page':100
        })
        data = json.loads(requests.get(query).text)
        totals = {}
        totals['total'] = data['paging']['total_items']
        totals['eps'] = data['data']
        return totals
### Utils para el MC. Mayor obtención de datos, y el año comienza desde julio
    def getCurrentMCYearStats(self, program, office_id):
        """
        Extrae el ma/re de el año MC actual (comenzando el anterior 1 de Julio, para un comité y uno de los 4 programas
        """
        now = datetime.now()
        currentYear = int(now.strftime('%Y'))
	if int(now.strftime('%m')) < 6:
	    currentYear -= 1
        startDate = "%d-07-01" % currentYear

        endDate = now.strftime('%Y-%m-%d')

        queryArgs = {
            'basic[home_office_id]':office_id,
            'basic[type]':self.ioDict[program[0]],
            'end_date':endDate,
            'programmes[]':self.programDict[program[1:]],
            'start_date':startDate
        }
        query = self._buildQuery(['applications', 'analyze.json'], queryArgs)
        response = json.loads(requests.get(query).text)['analytics']
        return {
            'applications': response['total_applications']['doc_count'],
            'accepted': response['total_matched']['doc_count'],
            'approved': response['total_approvals']['doc_count'],
            'realized': response['total_realized']['doc_count'],
            'completed': response['total_completed']['doc_count'],
            }

    def getCountryCurrentMCYearStats(self, program, mc=1551):
        """
        Extrae el ma/re de el año actual, para un comité y uno de los 4 programas
        """
        now = datetime.now()
        currentYear = int(now.strftime('%Y'))
	if int(now.strftime('%m')) < 6:
	    currentYear -= 1
        startDate = "%d-07-01" % currentYear

        endDate = now.strftime('%Y-%m-%d')

        queryArgs = {
            'basic[home_office_id]':mc,
            'basic[type]':self.ioDict[program[0].lower()],
            'end_date':endDate,
            'programmes[]':self.programDict[program[1:].lower()],
            'start_date':startDate
        }
        query = self._buildQuery(['applications', 'analyze.json'], queryArgs)
        try:
	    mcData = json.loads(requests.get(query).text)['analytics']
            lcData = mcData['children']['buckets']
            response = {}
            for lc in lcData:
                response[lc['key']] = {
                    'applications': lc['total_applications']['doc_count'],
                    'accepted': lc['total_matched']['doc_count'],
                    'approved': lc['total_approvals']['doc_count'],
                    'realized': lc['total_realized']['doc_count'],
                    'completed': lc['total_completed']['doc_count'],
		}
            response[mc] = {
                    'applications': mcData['total_applications']['doc_count'],
                    'accepted': mcData['total_matched']['doc_count'],
                    'approved': mcData['total_approvals']['doc_count'],
                    'realized': mcData['total_realized']['doc_count'],
                    'completed': mcData['total_completed']['doc_count'],
                }    

        except KeyError as e:
            print e
            print json.loads(requests.get(query).text)
            raise e
        return response
