from slugify import slugify
from ad_geo_backend.utils.common import AbstractTranslator


class Translator(AbstractTranslator):

    def translate(self, line):
        result = {'dolead_id': line['Criteria ID'],
                  'publisher_id': line['Criteria ID'],
                  'geo_type': line['Target Type'],
                  'country_code': line['Country Code'],
                  'name': line['Name'],
                  'slug': slugify(line['Name']),
                  'canonical_name': line['Canonical Name'],
                  }
        if line.get('Parent ID'):
            result['parent_id'] = line['Parent ID']
        self._enrich_w_coords(result['slug'], result)
        self._stats['translated'] += 1
        return result
