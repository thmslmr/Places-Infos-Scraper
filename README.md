# Places Infos Scrapper

Get information from a location or a list of locations.

Services currently supported:
  - Facebook
  - Wikipedia
  - Google places

Default configuration includes these three platforms.

Dependencies
---

    pip install python-google-places wikipedia


Settings
---

Insert your GooglePlaces and Facebook Graph API key in the `settings.json` file.  
You can also edit the field you wish to find for each service.

Examples of use
---

```python
    scraper = PlaceScraper()

    places = ['Paris', 'Eiffel Tower', 'Central Park']
    infos = scraper.scrap(places)
```
