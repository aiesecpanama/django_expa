# coding=utf-8
import json
import requests

#from django_podio.api import PodioApi

class ExpaApi:

    _apiUrl = "https://gis-api.aiesec.org/v1/{palabra1}/{palabra2}?access_token={token}"

    def __init__(self):
        self._login()
    

    def _login(self):
        self.token = requests.post("http://apps.aiesecandes.org/api/token").text
        return self.token

    def getToken(self):
        return self.token

    def getOpportunity(self, opId):
        response = requests.get(self._apiUrl.format(palabra1="opportunities", palabra2=opId, token=self.token))
        return response # + " " + self._apiUrl.format(palabra1="opportunities", palabra2=opId, token=self.token) + " " + self.token

    def test(self):
        api = PodioApi(14397108)
        items = api.getAllItems()
        for item in items:
            print item
            mail = json.loads(requests.get(self._apiUrl.format(palabra1="people", palabra2=item['values']['expa-id'], token=self.token)).text)["email"] #hace un request GET sobre la oportunidad con la ID dada, obtiene el texto, o lo transforma de json a un objeto de python
            print mail
            print api.updateItem(item['item'], {'correo': mail})
        

    def getOPManagersData(self, opId):
        """Éste método devuelve un diccionario con todos los EP Managers y sus datos de contacto de la oportunidad cuya ID entra como parámetro"""
        opportunity =  json.loads(requests.get(self._apiUrl.format(palabra1="opportunities", palabra2=opId, token=self.token)).text) #hace un request GET sobre la oportunidad con la ID dada, obtiene el texto, o lo transforma de json a un objeto de python
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
        
