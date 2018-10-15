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

    def __init__(self, slug_to_gps=None):
        self._stats = {'translated': 0, 'gps_coord_added': 0}
        self._slug_to_gps = slug_to_gps or {}

    def _enrich_w_coords(self, slug, result):
        if slug in self._slug_to_gps \
                and result['canonical_name'].endswith('France'):
            result['latitude'] = self._slug_to_gps[slug][0]
            result['longitude'] = self._slug_to_gps[slug][1]
            self._stats['gps_coord_added'] += 1

    def print_stats(self):
        logger.warning('translated %d elements', self._stats['translated'])
        logger.warning('added gps coords to %d elements',
                       self._stats['gps_coord_added'])


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
