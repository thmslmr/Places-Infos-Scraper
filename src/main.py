import json
import wikipedia
import requests
from googleplaces import GooglePlaces


class PlacesScrapper:

    def __init__(self, places):
        """ Init scrapper """
        if not places:
            raise Exception('Array of places must be provided.')

        self.input_places = places
        self.output_places = []
        self.settings = self.__fetch_settings()
        self.google_places = GooglePlaces(self.settings["google_api_key"])

    def __fetch_settings(self):
        """ Fetch settings from settings.json"""
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
        except FileNotFoundError:
            raise Exception('Sources file must be provided.')

        return settings

    def scrap(self):
        print("==== START ====")

        for place_name in self.input_places:
            place = self.get_google_info(place_name)
            place['wikipedia'] = self.get_wikipedia_infos(place_name)
            place['facebook'] = self.get_facebook_page_infos(place_name)
            self.output_places.append(place)
            self.dump_datas()
            print(place_name + ' : done !')

        print("==== END ====")

    def get_google_info(self, name):
        """
            Collect Google informations of the place with a text search request
            Return a associative array with its id - website - google map url
            - phone number - address
        """
        results = self.google_places.text_search(name)
        google_infos = {}

        if len(results.places) == 0:
            print(name + ' : Not found by Google Places!')
        else:
            matchObj = {
                'google_id': 'id',
                'website': 'website',
                'google_map_url': 'url',
                'phone_number': 'international_phone_number',
                'formatted_address': 'formatted_address'
            }

            place = results.places[0]
            place.get_details()
            for el in matchObj:
                try:
                    google_infos[el] = place.details[matchObj[el]]
                except KeyError:
                    google_infos[el] = False
            google_infos['name'] = name

        return google_infos

    def get_wikipedia_infos(self, name):
        """
            Collect Wikipedia informations of the place or of
            the first result of a Wikipedia research
            Return a associative array with its title
            page - wikipedia url - summmary
        """
        wiki_infos = {}
        results = wikipedia.search(name)

        if len(results) == 0:
            print(name + ' : Not found by Wikipedia !')
        else:
            try:
                page = wikipedia.page(name)
            except wikipedia.exceptions.PageError:
                page = wikipedia.page(results[0])

            wiki_infos['title'] = page.title
            wiki_infos['url'] = page.url
            wiki_infos['summary'] = page.summary

        return wiki_infos

    def get_facebook_page_infos(self, name):
        facebook_info = {}
        domain = 'https://graph.facebook.com/v2.8/'
        fb_access_token = self.settings['facebook_api_key']

        url_graph_search = domain + 'search?q=' + name + \
            '&fields=id,fan_count&type=page&access_token=' + fb_access_token
        res_search = requests.get(url_graph_search).json()

        if len(res_search['data']) == 0:
            print(name + ' : Not found by Facebook')
        else:
            target_page = self.get_max_fan_count_page(res_search['data'])

            url_graph_page = domain + target_page['id'] + \
                '?fields=about,cover,fan_count,general_info,link,name,\
                picture.type(large)&access_token=' + fb_access_token
            facebook_info = requests.get(url_graph_page).json()

        return facebook_info

    def get_max_fan_count_page(self, pages):
        max_fancount_page = pages[0]
        for el in pages:
            if el['fan_count'] > max_fancount_page['fan_count']:
                max_fancount_page = el
        return max_fancount_page
