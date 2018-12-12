import re
import logging
from slugify import slugify

from ad_geo_backend.backends.mongodb import MongoBackend
from ad_geo_backend.utils import file_utils

logger = logging.getLogger(__name__)
UPDATE_FREQ = 500
WRITE_BATCH_SIZE = 10000
SAINT_PATTERNS = ((re.compile(r'^st-'), 'saint-'),
                  (re.compile(r'-st-'), '-saint-'),
                  (re.compile(r'^ste-'), 'sainte-'),
                  (re.compile(r'-ste-'), '-sainte-'))


class AbstractTranslator:

    def __init__(self, slug_to_gps=None, gid_to_iso=None, alt_names=None,
                 cities=None):
        self._stats = {'translated': 0, 'gps_coord_added': 0,
                       'iso_code_added': 0, 'lang_added': 0,
                       }
        self._slug_to_gps = slug_to_gps or {}
        self._gid_to_iso = gid_to_iso or {}
        self._alt_names = alt_names or {}
        self._cities = cities or {}

    def _enrich_w_iso_code(self, google_id, result):
        if google_id in self._gid_to_iso:
            result['iso_code'] = self._gid_to_iso[google_id]
            self._stats['iso_code_added'] += 1
        # Maybe in the parent id?
        elif result.get('parent_id') in self._gid_to_iso:
            result['iso_code'] = self._gid_to_iso[result['parent_id']]
            self._stats['iso_code_added'] += 1
        # Maybe we are too deep and the parent is irrelevant so look for the
        # country code directly
        elif result.get('country_code') in self._gid_to_iso.values():
            result['iso_code'] = result['country_code']
            self._stats['iso_code_added'] += 1

    def _enrich_w_coords(self, slug, result):
        if slug in self._slug_to_gps \
                and result['canonical_name'].endswith('France'):
            result['latitude'] = self._slug_to_gps[slug][0]
            result['longitude'] = self._slug_to_gps[slug][1]
            self._stats['gps_coord_added'] += 1

    def _enrich_w_lang(self, result, country_code=None):
        name = result['name']
        if 'iso_code' not in result:
            # No iso_code, couldn't guess more...
            lang = []
        else:
            if country_code is None:
                country_code = result['iso_code']
                # Assuming region are set with - for Bing
                if '-' in country_code:
                    country_code = country_code.split('-')[0]
            geoname_id = self._cities.get((name.lower(), country_code.upper()))
            lang = self._alt_names.get(geoname_id, [])
        result['lang'] = lang
        if lang:
            self._stats['lang_added'] += 1

    def print_stats(self):
        print('translated ', self._stats['translated'], ' elements')
        print('added gps coords to ', self._stats['gps_coord_added'],
              ' elements')
        print('added iso code to ', self._stats['iso_code_added'], ' elements')
        print('added lang to ', self._stats['lang_added'], ' elements')


def parse_french_pc(french_pc_file):
    slug_to_gps = {}
    for city in file_utils.csv_to_dict(french_pc_file, delimiter=';'):
        if not city.get('coordonnees_gps'):
            continue
        gps_coords = tuple(city['coordonnees_gps'].split(', '))
        for key in ['Nom_commune', 'Libelle_acheminement',
                    'Ligne_5', 'Code_postal']:
            if not city.get(key):
                continue
            key = slugify(city[key])
            slug_to_gps[key] = gps_coords
            for pattern, long_form in SAINT_PATTERNS:
                if pattern.match(key):
                    slug_to_gps[pattern.sub(long_form, key)] = gps_coords
    return slug_to_gps


def parse_iso_codes(iso_codes_csv):
    iso_mapping = {}
    for iso_code in file_utils.csv_to_dict(iso_codes_csv):
        iso_mapping[iso_code['Google ID']] = iso_code['Iso Code']
    return iso_mapping


def parse_alt_names(alt_names_txt):
    alt_names = {}
    for alt_name in file_utils.txt_to_dict(alt_names_txt):
        geoname_id = alt_name[1]
        iso_language = alt_name[2].upper()
        name = alt_name[3]
        # Did not find enough data in the txt file for this one
        if not (geoname_id and iso_language and name):
            continue
        # Geonames include link to wikipedia and postal code
        if iso_language in ['LINK', 'POST']:
            continue

        if geoname_id in alt_names:
            alt_names[geoname_id].append({'lang': iso_language, 'name': name})
        else:
            alt_names[geoname_id] = [{'lang': iso_language, 'name': name}]
    return alt_names


def parse_cities(cities_txt):
    cities = {}
    for city in file_utils.txt_to_dict(cities_txt):
        geoname_id = city[0]
        name = city[1].lower()
        ascii_name = city[2].lower()
        country = city[8].upper()
        # Did not find enough data in the txt file for this one
        if not (geoname_id and name and country):
            continue
        cities[(name, country)] = geoname_id
        if name != ascii_name:
            cities[(ascii_name, country)] = geoname_id
    return cities


def correct_with_french_geoloc(network, cities, postal_codes):
    backend = MongoBackend(network)
    modified_cities, modified_pc = 0, 0

    logger.warning('adding lat/long to french cities')
    for index, slug in enumerate(cities):
        if not cities[slug]['coordonnees_gps']:
            continue
        if not index % UPDATE_FREQ:
            logger.warning('FRENCH CITIES modified/processed/total %d/%d/%d',
                           modified_cities, index, len(cities))
        lat, lng = cities[slug]['coordonnees_gps'].split(', ')
        result = backend.collection.update(
                {'country_code': 'FR', 'slug': slug},
                {'$set': {'latitude': lat, 'longitude': lng}})
        modified_cities += result['nModified']

    logger.warning('adding lat/long to french postal codes')
    for index, postal_code in enumerate(postal_codes):
        if not postal_codes[postal_code]['coordonnees_gps']:
            continue
        if not index % UPDATE_FREQ:
            logger.warning('FRENCH PC modified/processed/total %d/%d/%d',
                           modified_pc, index, len(cities))
        lat, lng = postal_codes[postal_code]['coordonnees_gps'].split(', ')
        result = backend.collection.update(
                {'country_code': 'FR', 'name': postal_code},
                {'$set': {'latitude': lat, 'longitude': lng}})
        modified_pc += result['nModified']

    logger.warning('Updated %d objects', modified_cities + modified_pc)


def load_file_to_backend(backend, csv_file, translator):
    lines = []
    for line in file_utils.csv_to_dict(csv_file):
        line = translator.translate(line)
        lines.append(line)
        if len(lines) >= WRITE_BATCH_SIZE:
            logger.info('writing %d lines into %s',
                        WRITE_BATCH_SIZE, backend.network)
            backend.insert_many(lines)
            lines = []
    if lines:
        backend.insert_many(lines)
        logger.info('writing %d lines into %s', len(lines), backend.network)
    translator.print_stats()
