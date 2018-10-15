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
    cmd_line = args.parse_args()

    MongoBackend.set_connection(cmd_line.db_host, cmd_line.db_name,
                                name=cmd_line.db_user,
                                password=cmd_line.db_pwd)
    return (cmd_line.google, cmd_line.bing, cmd_line.french_pc)
