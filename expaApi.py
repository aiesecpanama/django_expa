# coding=utf-8
import json
import requests
import urllib

import calendar
from datetime import datetime

#from django_podio.api import PodioApi

class ExpaApi:

    _apiUrl = "https://gis-api.aiesec.org/v1/{palabra1}/{palabra2}?access_token={token}"

    ioDict = {'i': 'opportunity', 'o': 'person'}
    programDict = {'gcdp': 1, 'gip': '2'}

    def __init__(self):
        self._login()
    

    def _login(self):
        self.token = requests.post("http://apps.aiesecandes.org/api/token").text
        return self.token

    def _buildQuery(self, routes, queryParams={}, version='v2'):
        """
            Builds a well-formed GIS API query
            
            version: The version of the API being used. Can be v1 or v2.
            routes: A list of the uri arguments (name better).
            queryParams: A dictionary of query parameters
        """
        baseUrl = "https://gis-api.aiesec.org/{version}/{routes}?{params}"
        queryParams['access_token'] = self.token
        return baseUrl.format(version=version, routes = "/".join(routes), params=urllib.urlencode(queryParams, True)) 

    def getToken(self):
        return self.token

    def getOpportunity(self, opID):
        response = requests.get(self._buildQuery(['opportunities', opID]))
        return response # + " " + self._apiUrl.format(palabra1="opportunities", palabra2=opId, token=self.token) + " " + self.token

    def test(self, **kwargs):
        return self.getColombiaContactList()

    def getManagedEPs(self, expaID):
        """
            Devuelve a todos los EPs que son administrados por el EP manager cuya EXPA ID entra como parámetro
       """
        response = requests.get(self._buildQuery(['people.json'], {'filters[managers][]':[expaID]})).text
        return response

    def getColombiaContactList(self):
        """
            Este método busca dentro de todas las oficinas locales del MC Colombia a los VPs de cada una de ellas para el término 2016
        """
        response = requests.get(self._buildQuery(['committees', '1551.json'])).text
        lcs = json.loads(response)['suboffices']
        ans = [] 
        counter = 0
        for lc in lcs:
            newLC = {'nombre':lc['full_name']}
            data = self.getLCEBContactList(str(lc['id']))
            newLC['cargos'] = data
            ans.append(newLC)
            counter += 1
            if counter==5:
                pass
                #break
        return ans 

    def getLCEBContactList(self, lcID):
        """
            Este método retorna un diccionario con las personas que conforman la junta ejecutiva del LC cuya ID entra como parámetro, para el periodo 2016
        """
        ans = [] 
        data = json.loads(requests.get(self._buildQuery(['committees', str(lcID), 'terms.json'])).text)
        for term in data['data']:
            if term['short_name'] == '2016':
                info = requests.get(self._buildQuery(['committees', str(lcID), 'terms', str(term['id']) + '.json']) ).text
                info = json.loads(info)
                for team in info['teams']:
                    if team["team_type"] == "eb": 
                        for position in team['positions']:
                            person = {}
                            if position['person_id'] is not None:
                                person = self.getContactData(json.loads(requests.get(self._buildQuery(['people', str(position['person_id']) + '.json'])).text))
                            person['cargo'] = position['position_name']
                            ans.append(person)
                        break
                break
        print ans
        return ans

    def getOPManagersData(self, opID):
        """Éste método devuelve un diccionario con todos los EP Managers y sus datos de contacto de la oportunidad cuya ID entra como parámetro"""
        opportunity =  json.loads(requests.get(self._buildQuery(['opportunities', opID])).text) #hace un request GET sobre la oportunidad con la ID dada, obtiene el texto, o lo transforma de json a un objeto de python
        managerData = opportunity["managers"]
        managers = [] 
        for manager in managerData:
            managerDict = {"name": manager["full_name"]}  
            contactData = {}
            if manager["contact_info"] is not None:#contact_info
                for key, value in manager["contact_info"].iteritems():
                    if value is not None:
                        contactData[key] = value
            contactData[u"altMail"] = manager["email"]
            managerDict["contactData"] = contactData
            managers.append(managerDict)
            
        return managers

    def getContactData(self, person):
        """
            Extrae los datos de contacto de una persona, a partir del objeto arrojado por la API de EXPA
        """
        personDict = {"name": person["full_name"]}  
        contactData = {}
        if person["contact_info"] is not None:#contact_info
            contactData = person['contact_info']
        contactData[u"altMail"] = person["email"]
        personDict["contactData"] = contactData
        return personDict

    def getMonthStats(self, month, year, program, lc = 1395):
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
        try:
            response = json.loads(requests.get(query).text)['analytics']
        except:
            print json.loads(requests.get(query).text)
        return {'MA': response['total_approvals']['doc_count'], 'RE': response['total_realized']['doc_count']}

    def getWeekStats(self, week, year, program, lc = 1395):
        """
            Extrae el ip/ma/re de un mes específico, en un año específico, para un comité y uno de los 4 programas
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
        try:
            response = json.loads(requests.get(query).text)['analytics']
        except:
            print json.loads(requests.get(query).text)
        return {'MA': response['total_approvals']['doc_count'], 'RE': response['total_realized']['doc_count']}

    def getLCWeeklyPerformance(self, lc=1395):
        now = datetime.now()
        currentWeek = int(now.strftime('%W'))
        currentYear = int(now.strftime('%Y'))
        answer = {}
        for io in ['i', 'o']:
            for program in ['gcdp', 'gip']:
                ma = []
                re = []
                maTotal = 0
                reTotal = 0
                for i in range (currentWeek+1):
                    weekData = self.getWeekStats(i, currentYear, io+program, lc)
                    ma.append(weekData['MA'])
                    maTotal += weekData['MA']
                    re.append(weekData['RE'])
                    reTotal += weekData['RE']
                totals = {'MATOTAL':maTotal, 'RETOTAL':reTotal}
                weekly = {'MA': ma, 'RE': re}
                answer[io+program] = {'totals': totals, 'weekly': weekly}
        return answer

    def getLCYearlyPerformance(self, year, lc=1395):
        """
            Returna el desempeño en matches y realizaciones de un LC en un año dado, separado por mes, para los cuatro programas
        """
        answer = {}
        for io in ['i', 'o']:
            for program in ['gcdp', 'gip']:
                ma = []
                re = []
                for i in range (1, 13):
                    monthData = self.getMonthStats(i, year, io+program)
                    print io + program + ', mes ' + str(i)
                    print monthData
                    ma.append(monthData['MA'])
                    re.append(monthData['RE'])
                answer[io+program] = {'MA': ma, 'RE': re}
        return answer
        
#Métodos relacionados con el año actual

    def getCurrentYearStats(self, program, lc = 1395):
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
            response = json.loads(requests.get(query).text)['analytics']
        except:
            print json.loads(requests.get(query).text)
        return {'MA': response['total_approvals']['doc_count'], 'RE': response['total_realized']['doc_count']}

    def getCountryCurrentYearStats(self, program, lc = 1551):
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

        except Exception as e:
            print e
            print json.loads(requests.get(query).text)
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

