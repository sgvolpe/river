__author__ = 'SG0216333'

import requests
import base64
import json
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

DEBUG = False
class Rest_Handler:
    token = None

    parameters = {"user": "7971", "group": "FF9A", "domain": "AA", "password": "WSPTS10"}
    URLS = {"PROD": "https://api.sabre.com", "CERT": "https://api.test.sabre.com"}

    def __init__(self, env="PROD", parameters=parameters, debug=False, token="", automaticAuth=True ):
        self.URL = self.URLS.get(env)
        self.parameters = parameters
        try:
            if token != "":
                self.token = token
            else:
                AuthenticationRS = self.AuthenticationRQ(self.URL, self.parameters)
                self.token = json.loads(AuthenticationRS.text)["access_token"]
        except:
            if DEBUG: print "Error while Authenticating"


    def encodeBase64(self, stringToEncode):
        return base64.b64encode(stringToEncode)


    def AuthenticationRQ(self, url, parameters, version='v2'):
        if version == 'v2': url = url + "/v2/auth/token"
        elif version == 'v1':
            url = url + "/v1/auth/token"
        user = parameters["user"]
        group = parameters["group"]
        domain = parameters["domain"]
        password = parameters["password"]
        encodedUserInfo =  self.encodeBase64("V1:" + user + ":" + group + ":" + domain)
        encodedPassword =  self.encodeBase64(password)
        encodedSecurityInfo = self.encodeBase64(encodedUserInfo + ":" + encodedPassword)

        data = {'grant_type':'client_credentials'}
        headers = {'content-type': 'application/x-www-form-urlencoded ','Authorization': 'Basic ' + encodedSecurityInfo, 'Accept-Encoding': 'gzip,deflate'}
        response = requests.post(url, headers=headers,data=data)
        if(response.status_code != 200):
            if DEBUG: print "ERROR: I couldnt authenticate"
            self.token = json.loads(response.text)["access_token"]

        return response


    def BargainFinderMaxRQ(self, payload, debug=False, token='', version='3.3.0', others=''):
        if token != '':
            self.token = token
        url = self.URL + "/v"+version+"/shop/flights?mode=live"
        if(debug): url += "&debug=true"
        if others != '': url += others
        data = payload
        headers = {'content-type': 'application/json','Authorization': 'Bearer ' + str(self.token)}

        response = requests.post(url, headers=headers,data=data)
        return response

    def AlternateDateRQ(self, payload, debug=False, token=None, version='3.3.0'):
        url = self.URL + "/v"+version+"/shop/altdates/flights?mode=live"
        if(debug): url += "&debug=true"
        data = payload
        headers = {'content-type': 'application/json','Authorization': 'Bearer ' + str(self.token)}
        response = requests.post(url, headers=headers,data=data)
        return response


    def AdvancedCalendarSearchRQ(self, payload, debug=False, token=None, version='3.3.0', pos='US'):
        url = self.URL + "/v"+version+"/shop/calendar/flights?"
        url += "pointofsalecountry=" + pos
        if(debug): url += "&debug=true"
        data = payload
        headers = {'content-type': 'application/json','Authorization': 'Bearer ' + str(self.token)}
        response = requests.post(url, headers=headers,data=data)
        return response

    def AlternateAirportShopRQ(self, payload, debug=False, token=None, version='3.3.0'):
        url = self.URL + "/v"+version+"/shop/altairports/flights?mode=live"
        if(debug): url += "&debug=true"
        data = payload
        headers = {'content-type': 'application/json','Authorization': 'Bearer ' + str(self.token)}
        response = requests.post(url, headers=headers,data=data)
        return response



    def InstaFlightSearch(self, url_parameters ):
        url = self.URL + url_parameters
        headers = {'Authorization': 'Bearer ' + str(self.token)}
        response = requests.get(url, headers=headers)
        return response

    def GenericRestCall(self, url, payload, method='POST' ):
        url =  url
        headers = {'Authorization': 'Bearer ' + str(self.token)}
        if method =='GET':
            response = requests.get(url, headers=headers)
        if method == 'POST':
            data = payload
            response = requests.post(url, headers=headers,data=data)
        return response





