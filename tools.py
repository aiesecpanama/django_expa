from __future__ import unicode_literals

def getContactData(person):
    """
        Extrae los datos de contacto de una persona, a partir del objeto arrojado por la API de EXPA
    """
    personDict = {"name": person["full_name"]}
    contactData = {}
    if person["contact_info"] is not None:
        contactData = person['contact_info']
    contactData["altMail"] = person["email"]
    personDict["contactData"] = contactData
    return personDict
