# -*- coding: utf-8 -*-

# Imports
import json, wikipedia, requests
from wikipedia.exceptions import *
from googleplaces import GooglePlaces, types, lang


class PlacesScrapper :

    output_places = input_places = []
    google_places = None
    input_file = output_file = ''
    settings = {}

    def __init__(self, input_file='input.json', output_file='output.json') :
        self.input_file = input_file
        self.output_file = output_file
        self.loadDatas()

        with open('settings.json', encoding='utf8') as set_file :
            self.settings = json.load(set_file)
        self.google_places = GooglePlaces(self.settings["google_api_key"])

    def loadDatas(self) :
        with open(self.input_file, encoding='utf8') as input_file :
            self.input_places = json.load(input_file)

    def dumpDatas(self):
        with open(self.output_file, 'w', encoding='utf8') as output_file :
            json.dump(self.output_places, output_file, ensure_ascii=False)

    def scrap(self) :
        print("==== START ====")

        for place_name in self.input_places :
            place = self.getGoogleInfo(place_name)
            place['wikipedia'] = self.getWikipediaInfos(place_name)
            place['facebook'] = self.getFacebookPageInfos(place_name)
            self.output_places.append(place)
            self.dumpDatas()
            print(place_name + ' : done !')

        print("==== END ====")

    def getGoogleInfo(self, name):
        """
            Collect Google informations of the place with a text search request
            Return a associative array with its id - website - google map url - phone number - address
        """
        results = self.google_places.text_search(name)
        google_infos = {}

        if len(results.places) == 0 :
            print(name + ' : Not found by Google Places!')
            return google_infos

        matchObj = {
            'google_id' : 'id',
            'website' : 'website',
            'google_map_url' : 'url',
            'phone_number' : 'international_phone_number',
            'formatted_address' : 'formatted_address'
        }

        place = results.places[0]
        place.get_details()
        for el in matchObj :
            try :
                google_infos[el] = place.details[matchObj[el]]
            except KeyError :
                google_infos[el] = False
        google_infos['name'] = name;
        return infos

    def getWikipediaInfos(self, name):
        """
            Collect Wikipedia informations of the place or of the first result of a Wikipedia research
            Return a associative array with its title page - wikipedia url - summmary
        """
        wiki_infos = {}
        results = wikipedia.search(name)

        if len(results) == 0 :
            print(name + ' : Not found by Wikipedia !')
            return wiki_infos

        try :
            page = wikipedia.page(name)
        except PageError:
            page = wikipedia.page(results[0])

        wiki_infos['title'] = page.title
        wiki_infos['url'] = page.url
        wiki_infos['summary'] = page.summary

        return wiki_infos

    def getFacebookPageInfos(self, name) :
        facebook_info = {}
        domain = 'https://graph.facebook.com/v2.8/'
        fb_access_token = self.settings['facebook_api_key']

        url_graph_search = domain +'search?q='+el['name']+'&fields=id,fan_count&type=page&access_token=' + fb_access_token
        res_search = requests.get(url_graph_search).json()

        if len(res_search) == 0:
            print(name + ' : Not found by Facebook')
            return facebook_info

        target_page = getMaxFanCountPage(res_search['data'])
        url_graph_page = domain + target_page['id'] + '?fields=about,cover,fan_count,general_info,link,name,picture&access_token=' + fb_access_token
        facebook_info = requests.get(url_graph_page).json()

        return facebook_info

    def getMaxFanCountPage(self, pages) :
        max_fancount_page = pages[0]
        for el in pages :
            if el['fan_count'] > max_fancount_page['fan_count'] :
                max_fancount_page = el
        return max_fancount_page
