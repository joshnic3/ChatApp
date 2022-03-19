import sys
import argparse
import yaml
from lib.database import DAO


class DatabaseManager:

    def __init__(self, database_path):
        self.dao = DAO(database_path)

    def create_tables(self, sql_dict):
        for table, sql in sql_dict.items():
            print(f'Creating table {table}...')
            self.dao.execute(sql)

    def insert_rows(self, rows_dict):
        for table, rows in rows_dict.items():
            print(f'Inserting {len(rows)} into table {table}...')
            self.dao.insert_many(table, rows)


def parse_configs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--schema', type=str, required=True)
    args = parser.parse_args()
    with open(args.schema, "r") as stream:
        try:
            yaml_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return yaml_dict


def main():
    configs = parse_configs()
    dbm = DatabaseManager(configs.get('path'))
    dbm.create_tables(configs.get('sql'))
    if configs.get('rows'):
        dbm.insert_rows(configs.get('rows'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
