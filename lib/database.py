import sqlite3


def _list_to_str(value):
    return [str(v) if v is not None else None for v in value]


def _wildcards(values):
    return ", ".join(["?" for _ in values])


def _where_sql(keys):
    return f' WHERE {" AND ".join([f"{k} = ?" for k in keys])}'


def _set_sql(keys):
    return f' SET {", ".join([f"{k} = ?" for k in keys])}'


class DAO:

    def __init__(self, file_path):
        # TODO Almost definitely not thread safe!
        self.connection = sqlite3.connect(file_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys = ON;')

    def execute(self, sql, params=(), return_one=False):
        results = self.cursor.execute(sql, params)
        self.connection.commit()
        return results.fetchone() if return_one else results.fetchall()

    def insert(self, table, row):
        row = [None] + row
        self.execute(f'INSERT INTO {table} VALUES ({_wildcards(row)});', _list_to_str(row))
        return self.execute('SELECT last_insert_rowid();', return_one=True)

    def insert_many(self, table, rows):
        for row in rows:
            row = [None] + row
            self.execute(f'INSERT INTO {table} VALUES ({_wildcards(row)});', _list_to_str(row))

    def select(self, table, condition, return_one=False):
        return self.execute(
            f'SELECT * FROM {table}{_where_sql(condition.keys())};',
            list(condition.values()),
            return_one
        )

    def update(self, table, values, condition):
        return self.execute(
            f'UPDATE {table} {_set_sql(values.keys())}{_where_sql(condition.keys())};',
            list(values.values()) + list(condition.values())
        )

    def delete(self, table, condition):
        return self.execute(f'DELETE FROM {table}{_where_sql(condition.keys())};', list(condition.values()))