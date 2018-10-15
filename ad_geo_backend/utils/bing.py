import logging
from slugify import slugify
from ad_geo_backend.utils.common import AbstractTranslator

logger = logging.getLogger(__name__)


class Translator(AbstractTranslator):

    def __init__(self, slug_to_gps=None):
        self.parents = {}
        super().__init__(slug_to_gps)

    def translate(self, line):
        names = line['Bing Display Name'].split('|')
        dolead_id = line['AdWords Location Id'] \
                or 'bing_%s' % line['Location Id']
        self.parents[tuple(names)] = dolead_id

        result = {'dolead_id': dolead_id,
                  'publisher_id': line['Location Id'],
                  'geo_type': line['Location Type'],
                  'name': names[0],
                  'slug': slugify(names[0]),
                  'canonical_name': line['Bing Display Name'],
                  'google_ref': bool(line.get('AdWords Location Id')),
                  }

        if len(names) > 1:
            result['parent_id'] = self.parents[tuple(names[1:])]
            result['top_level'] = names[-1]

        self._enrich_w_coords(result['slug'], result)
        self._stats['translated'] += 1
        return result


def correct_with_google_data(bing_backend, google_backend):
    logger.warning('adding country code to bing datas')
    country_codes = {country.name: country.country_code
            for country in google_backend.list({'geo_type': 'Country'})}

    for index, name in enumerate(country_codes):
        if not index % 50:
            logger.warning('added %d/%d codes', index, len(country_codes))
        bing_backend.collection.update({'top_level': name},
                {'$set': {'country_code': country_codes[name]}}, multi=True)
    logger.warning('added %d/%d codes', len(country_codes), len(country_codes))
