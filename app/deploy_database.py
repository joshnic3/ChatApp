import argparse
import logging
import logging.config
import sys

import yaml

from lib.database import DAO


class DatabaseManager:

    def __init__(self, database_path):
        self.dao = DAO(database_path)

    def create_tables(self, sql_dict):
        for table, sql in sql_dict.items():
            self.dao.execute(sql)
            logging.info(f'Created table {table}.')

    def insert_rows(self, rows_dict):
        for table, rows in rows_dict.items():
            self.dao.insert_many(table, rows)
            logging.info(f'Inserted {len(rows)} into table {table}.')


def parse_configs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configs', type=str, required=True)
    args = parser.parse_args()
    with open(args.configs, "r") as stream:
        try:
            yaml_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return yaml_dict


def main():
    configs = parse_configs()
    logging.config.dictConfig(configs.get('log'))
    dbm = DatabaseManager(configs.get('database').get('path'))
    dbm.create_tables(configs.get('database').get('tables'))
    if configs.get('database').get('rows'):
        dbm.insert_rows(configs.get('database').get('rows'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
