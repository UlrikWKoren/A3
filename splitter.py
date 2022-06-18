import json
import pprint

with open("countries.geojson", 'r', encoding="utf-8") as file:
    data = json.load(file)

    for country in data['features']:
        pprint.pprint(country['properties']['ADMIN'])

        with open(f"geojson-files/{country['properties']['ADMIN']}.geojson", 'w', encoding='utf-8') as file2:
            json.dump(country,file2)
