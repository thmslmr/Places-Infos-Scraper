# Places Infos Scrapper

Recupérer les informations sur different service d'un lieu ou d'une liste de lieu.

Services actuellement disponible:
    - facebook
    - wikipedia
    - Google places

Dependencies
---

    pip install python-google-places wikipedia


Settings
---

Insert your GooglePlaces and Facebook Graph API key in the `settings.json` file.  
Vous pouvez aussi modifier les champs que vous souhaitez récupérer pour chaque services.

Examples of use
---

```python
    scraper = PlaceScraper()

    places = ['Paris', 'Tour Eiffel', 'Central Parc']
    infos = scraper.scrap(places)
```
