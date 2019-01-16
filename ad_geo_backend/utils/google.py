from slugify import slugify
from pymongo import ReplaceOne

from ad_geo_backend.utils.common import (AbstractTranslator, SAINT_PATTERNS)
from ad_geo_backend.utils import file_utils


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
        self._enrich_w_iso_code(line['Criteria ID'], result)
        self._enrich_w_lang_n_pop(result, result['country_code'])
        self._stats['translated'] += 1
        return result


def get_all_names(line):
    yield slugify(line['Nom_commune'])
    name = slugify(line['Nom_commune'])
    for pattern, long_form in SAINT_PATTERNS:
        name = pattern.sub(long_form, name)
    yield name
    yield slugify(line['Libelle_acheminement'])
    name = slugify(line['Libelle_acheminement'])
    for pattern, long_form in SAINT_PATTERNS:
        name = pattern.sub(long_form, name)
    yield name
    if line['Ligne_5']:  # linking old name
        yield slugify(line['Ligne_5'])


def correct_fr_hierarchy(backend, french_pc_file=None):
    """
    Try to connect FR cities & department as far as we can
    """
    if french_pc_file is None:
        return

    deps = {}
    cities = {}
    ops = []

    for dep in backend.collection.find({'country_code': 'FR',
                                        'geo_type': 'Department'}):
        if 'FR-' in dep['iso_code']:
            deps[dep['iso_code'].split('-')[1]] = dep
        else:
            deps[dep['iso_code']] = dep

    # Constructing mapping
    for city in file_utils.csv_to_dict(french_pc_file, delimiter=';'):
        city_d = {'dep_no': city['Code_commune_INSEE'][:2],
                  }

        if city_d['dep_no'].startswith('0'):
            city_d['dep_no'] = city_d['dep_no'][1]

        if city_d['dep_no'] in {'97', '98', '99'}:
            continue

        for name in get_all_names(city):
            key = "%s-%s" % (deps[city_d['dep_no']]['parent_id'], name)
            cities[key] = city_d

    # Browsing collection to update when possible
    for city in backend.collection.find({'country_code': 'FR',
                                         'geo_type': 'City'}):
        cdata = cities.get('%s-%s' % (city['parent_id'], city['slug']))
        if cdata is None:
            continue
        if cdata['dep_no'] not in deps:
            continue
        city['parent_id'] = deps[cdata['dep_no']]['dolead_id']
        ops.append(ReplaceOne({'_id': city['_id']}, city))

    if ops:
        print('%s/%s FR hierarchy corrected' % (
            len(ops), backend.collection.find({'country_code': 'FR',
                                               'geo_type': 'City'}).count()))
        backend.collection.bulk_write(ops)


def correct_es_hierarchy(backend, spain_pc_file=None):
    """
    Try to connect ES cities & provinces as far as we can
    """
    if spain_pc_file is None:
        return

    provs = {}
    cities = {}
    ops = []

    def _get_all_names(line):
        yield line[2]
        line_name = line[2]
        if '/' in line_name:
            for name in line_name.split('/'):
                yield name.strip()

    for prov in backend.collection.find({'country_code': 'ES',
                                        'geo_type': 'Province'}):
        if 'ES-' in prov['iso_code']:
            provs[prov['iso_code'].split('-')[1]] = prov
        else:
            provs[prov['iso_code']] = provs

    # Constructing mapping
    for city in file_utils.txt_to_dict(spain_pc_file):
        city_d = {'province': city[4],
                  }

        for name in _get_all_names(city):
            try:
                key = "%s-%s" % (provs[city_d['province']]['parent_id'],
                                 name.lower())
            except KeyError:
                # Province did not exist in our Adwords file
                continue
            cities[key] = city_d

    # Browsing collection to update when possible
    for city in backend.collection.find({'country_code': 'ES',
                                         'geo_type': 'City'}):
        cdata = cities.get('%s-%s' % (city['parent_id'], city['name'].lower()))
        if cdata is None:
            continue
        if cdata['province'] not in provs:
            continue
        city['parent_id'] = provs[cdata['province']]['dolead_id']
        ops.append(ReplaceOne({'_id': city['_id']}, city))

    if ops:
        print('%s/%s ES hierarchy corrected' % (
            len(ops), backend.collection.find({'country_code': 'ES',
                                               'geo_type': 'City'}).count()))
        backend.collection.bulk_write(ops)
