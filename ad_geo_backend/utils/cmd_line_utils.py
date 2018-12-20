from argparse import ArgumentParser
from ad_geo_backend.backends.mongodb import MongoBackend


def parse_args():
    args = ArgumentParser("load data into backends")
    args.add_argument('db_host')
    args.add_argument('db_name')
    args.add_argument('db_user')
    args.add_argument('db_pwd')
    args.add_argument('--google', default=None)
    args.add_argument('--bing', default=None)
    args.add_argument('--french-pc', dest='french_pc', default=None)
    args.add_argument('--spain-pc', dest='spain_pc', default=None)
    args.add_argument('--iso-code', dest='iso_codes', default=None,
                      help='a mapping Google IDsto ISO Codes')
    args.add_argument('--alternate-names', dest='alt_names', default=None,
                      help='alternate city name from GeoNames')
    args.add_argument('--geonames-cities', dest='cities', default=None,
                      help='cities txt coming from GeoNames')
    cmd_line = args.parse_args()

    MongoBackend.set_connection(cmd_line.db_host, cmd_line.db_name,
                                name=cmd_line.db_user,
                                password=cmd_line.db_pwd)
    return (cmd_line.google, cmd_line.bing, cmd_line.french_pc,
            cmd_line.spain_pc, cmd_line.iso_codes, cmd_line.alt_names,
            cmd_line.cities)
