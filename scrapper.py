# -*- coding: utf-8 -*-

# Imports
import json, wikipedia
from wikipedia.exceptions import *
from googleplaces import GooglePlaces, types, lang


class PlacesScrapper :

    output_places = input_places = []
    google_places = None
    input_file = output_file = ''

    def __init__(self, input_file='input.json', output_file='output.json') :
        self.input_file = input_file
        self.output_file = output_file
        self.loadDatas()

        with open('settings.json', encoding='utf8') as set_file :
            settings = json.load(set_file)
        self.google_places = GooglePlaces(settings["google_api_key"])

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
        infos = {}

        if len(results.places) == 0 :
            print(name + ' : Not found by Google Places!')
            return {}

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
                infos[el] = place.details[matchObj[el]]
            except KeyError :
                infos[el] = False
        infos['name'] = name;
        return infos

    def getWikipediaInfos(self, name):
        """
            Collect Wikipedia informations of the place or of the first result of a Wikipedia research
            Return a associative array with its title page - wikipedia url - summmary
        """
        wiki_info = {}
        results = wikipedia.search(name)

        if len(results) == 0 :
            return wiki_info
            print(name + ' : Not found by Wikipedia !')

        try :
            page = wikipedia.page(name)
        except PageError:
            page = wikipedia.page(results[0])

        wiki_info['title'] = page.title
        wiki_info['url'] = page.url
        wiki_info['summary'] = page.summary

        return wiki_info
