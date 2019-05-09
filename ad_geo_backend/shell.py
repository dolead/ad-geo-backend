import logging
from ad_geo_backend.backends.mongodb import MongoBackend
from ad_geo_backend.backends.geonames_db import MongoGeonamesBackend
from ad_geo_backend.utils import common, bing, google, cmd_line_utils

logger = logging.getLogger(__name__)


def load():
    google_file, bing_file, french_pc_file, spain_pc_file, iso_code_file, \
        alt_names, cities = cmd_line_utils.parse_args()

    geonames_backend = MongoGeonamesBackend('GEONAMES')
    google_backend = MongoBackend('GOOGLE')
    bing_backend = MongoBackend('BING')

    # A. Load GeoNames db
    if cities:
        print('Will fill GeoNames collection')
        geonames_backend.reset()
        geonames_backend.check_indexes()
        common.fill_geo_data(geonames_backend, cities)

    # B. Add lang/translations
    if alt_names:
        print('Will map translated names on GeoNames collection')
        common.fill_lang_geo(geonames_backend, alt_names)

    geonames_backend.close_connection()

    slug_to_gps = None
    if french_pc_file:
        slug_to_gps = common.parse_french_pc(french_pc_file)

    iso_code_mapping = None
    if iso_code_file:
        iso_code_mapping = common.parse_iso_codes(iso_code_file)

    alt_names_mapping = None
    cities_mapping = None
    if alt_names and cities:
        alt_names_mapping = common.parse_alt_names(alt_names)
        cities_mapping = common.parse_cities(cities)

    # C. Load Google backend
    if google_file:
        google_backend.reset()
        google_backend.check_indexes()
        google_trans = google.Translator(slug_to_gps, iso_code_mapping,
                                         alt_names_mapping, cities_mapping)

        common.load_file_to_backend(google_backend, google_file, google_trans)
        google.correct_fr_hierarchy(google_backend, french_pc_file)
        google.correct_es_hierarchy(google_backend, spain_pc_file)

    # D. Load Bing backend
    if bing_file:
        bing_backend.reset()
        bing_backend.check_indexes()
        bing_trans = bing.Translator(slug_to_gps, iso_code_mapping,
                                     alt_names_mapping, cities_mapping)

        common.load_file_to_backend(bing_backend, bing_file, bing_trans)
        bing.correct_with_google_data(bing_backend, google_backend)

    google_backend.close_connection()
    bing_backend.close_connection()
