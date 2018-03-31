import json
import wikipedia
import requests
from googleplaces import GooglePlaces


class PlaceScraper:

    def __init__(self,
                 services=['facebook', 'wikipedia', 'google'],
                 settings_file='settings.json'):
        """ Init scrapper """
        if not isinstance(services, list):
            raise Exception('Services must be a list.')

        self.settings = self.__fetch_settings(settings_file)
        self.services = [service for service in services
                         if service in self.settings['services'].keys()]
        if not services:
            raise Exception('List of available services must be provided.')

    def __fetch_settings(self, file_name):
        """ Fetch settings from settings.json"""
        if not file_name:
            raise Exception('Settings file name must be provided.')

        try:
            with open(file_name, 'r') as file:
                settings_file = json.load(file)
        except FileNotFoundError:
            raise Exception('Settings file must be provided.')

        try:
            settings = settings_file['placescrapper']
        except KeyError:
            raise Exception('Settings file must contain \
            `placescraper` settings.')

        return settings

    def __get_settings(self, path):
        """ Get settings with dot path """
        if not path:
            raise Exception('Setting key must be provided')

        res = self.settings

        for key in path.split('.'):
            res = res.get(key, {})

        return res

    def get_google_infos(self, name):
        """ Get Google infos of the first place for a given name """
        if not name:
            raise Exception('Place name must be provided.')

        api_key = self.__get_settings("services.google.api_key")
        gp = GooglePlaces(api_key)
        results = gp.text_search(name)

        if not results.places:
            raise Exception('Place not found by Google.')

        place = results.places[0]
        place.get_details()

        return {info: place.details.get(info) for info
                in self.__get_settings('services.google.infos')}

    def get_wikipedia_infos(self, name):
        """ Get Wikipedia infos of the first place for a given name """
        if not name:
            raise Exception('Place name must be provided.')

        results = wikipedia.search(name)

        if not results:
            raise Exception('Place not found by Wikipedia.')

        page = wikipedia.page(results[0])

        return {info: page[info] for info
                in self.__get_settings('services.wikipedia.infos')}

    def get_facebook_infos(self, name):
        """ Get Facebook infos for a given place name """
        if not name:
            raise Exception('Place name must be provided.')

        domain = "https://graph.facebook.com/v2.8/"
        fb_access_token = self.__get_settings('services.facebook.api_key')

        search_url = domain + 'search?q=' + name + \
            '&fields=id,fan_count&type=page&access_token=' + fb_access_token

        search_results = requests.get(search_url).json()

        if not search_results:
            raise Exception('Place not found by Facebook.')

        page = max(search_results['data'], key=lambda x: x['fan_count'])
        fields = ','.join(self.__get_settings('services.facebook.infos'))
        url = '{0}{1}?fields={2}&access_token={3}'.format(
            domain, page['id'], fields, fb_access_token)

        return requests.get(url).json()

    def scrap(self, places):
        """ Main function """
        if not places:
            raise Exception('Places must be provided.')

        if not isinstance(places, list):
            places = [places]

        return [{"name": place, "infos": {
            service: getattr(self, 'get_{0}_infos'.format(service))(place)
            for service in self.services}}
            for place in places]
