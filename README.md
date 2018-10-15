# Ad Geo Backend

The purpose of this package is to store and enhance Geo data from [Adwords](https://developers.google.com/adwords/api/docs/appendix/geotargeting) and [BingAds](https://docs.microsoft.com/en-us/bingads/guides/geographical-location-codes?view=bingads-12).

You can enhance french location by supplying a CSV listing french cities and there GPS coordinates available [here](https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/).

### Warning

* AdWords and Bing data are stored in separate collections
* Supplying either ```--google``` or ```--bing``` will reset either collection

## Installation

```bash
pip install ad-geo-backend
```

## Development

```bash
python setup.py develop
```

## Feeding AdGeoBackend

```bash
load-geo-data amongo01.raws jenkins_geo jenkins jenkins --google google.csv --bing bing.csv --frenc-pc laposte_hexasmal.csv
```

## Using the backend

```python
>>> from ad_geo_backend import GeoBackend
>>> GeoBackend.set_connection(host, db_name, name=login, password=password)
>>> list(ad_geo_backend.GeoBackend('BING').list({'name': 'Bourgogne'}))
[<State #20315 [FR] Bourgogne>, <City #bing_15201 [FR] Bourgogne>]
>>> list(ad_geo_backend.GeoBackend('BING').list({'name': 'Paris'}))
[<MetroArea #bing_4321 [FR] Paris>, <City #bing_5202 [CA] Paris>, <City #1006094 [FR] Paris>, <City #1013312 [None] Paris>, <City #1016210 [None] Paris>, <City #1016756 [None] Paris>, <City #1017861 [None] Paris>, <City #1018992 [None] Paris>, <City #1020534 [None] Paris>, <City #bing_60439 [None] Paris>, <City #1026100 [None] Paris>, <City #1026678 [None] Paris>]
>>> list(ad_geo_backend.GeoBackend('BING').list({'name': 'Paris'}))
[<MetroArea #bing_4321 [FR] Paris>, <City #bing_5202 [CA] Paris>, <City #1006094 [FR] Paris>, <City #1013312 [None] Paris>, <City #1016210 [None] Paris>, <City #1016756 [None] Paris>, <City #1017861 [None] Paris>, <City #1018992 [None] Paris>, <City #1020534 [None] Paris>, <City #bing_60439 [None] Paris>, <City #1026100 [None] Paris>, <City #1026678 [None] Paris>]
>>> list(ad_geo_backend.GeoBackend('GOOGLE').list({'name': 'Paris', 'country_code': 'FR'}))
[<City #1006094 [FR] Paris>, <Department #9040871 [FR] Paris>]
>>> list(ad_geo_backend.GeoBackend('GOOGLE').list({'name': 'Paris', 'country_code': 'FR', 'geo_type': 'City'}))
[<City #1006094 [FR] Paris>]
```
