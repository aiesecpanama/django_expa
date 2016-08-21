#encoding:utf-8
from __future__ import unicode_literals

def getContactData(person):
    """
        Extrae los datos de contacto de una persona, a partir del objeto arrojado por la API de EXPA
    """
    personDict = {"name": person["full_name"], 'expaID': person['id']}
    contactData = {}
    try:
        if person['contact_info'] is not None: #Para evitar una excepción
            contactData = person['contact_info']
    except KeyError:
        pass
    contactData["altMail"] = person["email"]
    personDict["contactData"] = contactData
    return personDict
