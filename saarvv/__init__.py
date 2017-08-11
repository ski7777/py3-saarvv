#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import urllib.request
import json


class SaarVV():

    def __init__(self, url):
        if url == '':
            raise ValueError('No saarfahrplan URL given')
        self.BaseUrl = url
        if not self.BaseUrl.endswith('/'):
            self.BaseUrl = self.BaseUrl + '/'

    def call_server_json(self, call):
        raw = self.call_server(call)
        raw = '{' + raw.split('{', 1)[1][::-1].split('}', 1)[1][::-1] + '}'
        data = json.loads(raw)
        return(data)

    def call_server(self, call):
        print('Loading: ' + self.BaseUrl + call)
        data = urllib.request.urlopen(self.BaseUrl + call).read().decode('utf-8', 'replace')
        return(data)

    class SearchResultChildObject():
        def __init__(self, data):
            if type(data) != dict:
                raise ValueError('SearchResultChildObject input data was not type dict')
            self.data = data

        def getName(self):
            return(self.data['value'])

        def getID(self):
            return(int(self.data['extID']))

        def getType(self):
            return(int(self.data['type']))

        def getQueryData(self):
            return(self.data['id'])

    class SearchResultObject():
        def __init__(self, parent, data):
            self.parent = parent
            if type(data) != dict:
                raise ValueError('SearchResultObject input data was not type dict')
            self.data = data
            if 'suggestions' not in self.data.keys():
                raise ValueError('SearchResultObject needs key suggestions')
            self.data = self.data['suggestions']

        def __getitem__(self, i):
            if len(self) - 1 < i:
                raise IndexError('Search result index out of range')
            return(self.parent.SearchResultChildObject(self.data[i]))

        def __len__(self):
            return(len(self.data))

        def getBestResult(self):
            if len(self) == 0:
                raise KeyError('No results found')
            return(self[0])

        def getBestResultType(self, t):
            i = 0
            while i < len(self):
                result = self[i]
                if result.getType() == t:
                    return(result)
                i += 1
            raise KeyError('No results found')

        def getBestResultTypeStop(self):
            return(self.getBestResultType(1))

        def getBestResultTypePOI(self):
            return(self.getBestResultType(4))

    def searchStations(self, searchString):
        url = 'cgi-bin/ajax-getstop.exe/dny'
        parm = {
            'start': 1,
            'tpl': 'suggest2json',
            'REQ0JourneyStopsS0A': 255,
            'getstop': 1,
            'noSession': 'yes',
            'REQ0JourneyStopsS0G': searchString
        }
        stations = self.call_server_json(url + '?' + self.dict2httpGETString(parm))
        return(self.SearchResultObject(self, stations))

    def dict2httpGETString(self, data):
        retList = []
        for x, y in data.items():
            retList.append(x + '=' + str(y))
        return('&'.join(retList))
