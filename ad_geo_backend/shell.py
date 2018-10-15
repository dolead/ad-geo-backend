import logging
from ad_geo_backend.backends.mongodb import MongoBackend
from ad_geo_backend.utils import common, bing, google, cmd_line_utils

logger = logging.getLogger(__name__)


def load():
    google_file, bing_file, french_pc_file = cmd_line_utils.parse_args()
    google_backend = MongoBackend('GOOGLE')
    bing_backend = MongoBackend('BING') if bing_file else None

    if french_pc_file:
        slug_to_gps = common.parse_french_pc(french_pc_file)
        google_trans = google.Translator(slug_to_gps)
        bing_trans = bing.Translator(slug_to_gps)
    else:
        google_trans = google.Translator()
        bing_trans = bing.Translator()

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
