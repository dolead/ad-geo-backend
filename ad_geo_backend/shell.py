import logging
from ad_geo_backend.backends.mongodb import MongoBackend
from ad_geo_backend.utils import common, bing, google, cmd_line_utils

logger = logging.getLogger(__name__)


def load():
    google_file, bing_file, french_pc_file, iso_code_file \
            = cmd_line_utils.parse_args()
    google_backend = MongoBackend('GOOGLE')
    bing_backend = MongoBackend('BING') if bing_file else None

    slug_to_gps = None
    if french_pc_file:
        slug_to_gps = common.parse_french_pc(french_pc_file)

    iso_code_mapping = None
    if iso_code_file:
        iso_code_mapping = common.parse_iso_codes(iso_code_file)
    google_trans = google.Translator(slug_to_gps, iso_code_mapping)
    bing_trans = bing.Translator(slug_to_gps, iso_code_mapping) \
            if bing_file else None

    if google_file:
        google_backend.reset()
        google_backend.check_indexes()
        common.load_file_to_backend(google_backend, google_file, google_trans)
    if bing_file:
        bing_backend = MongoBackend('BING')
        bing_backend.reset()
        bing_backend.check_indexes()
        common.load_file_to_backend(bing_backend, bing_file, bing_trans)
        bing.correct_with_google_data(bing_backend, google_backend)
