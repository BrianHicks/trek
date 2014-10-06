# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from psycopg2 import connect, ProgrammingError
import re


class PostgresRunner(object):
    parser = ArgumentParser('postgres')
    parser.add_argument(
        'uri',
        help='URI to the Postgres database to migrate'
    )

    uri_re = re.compile(
        r'^postgres://' \
        r'(?P<user>\S+?)(:(?P<password>\S+?))?@' \
        r'(?P<hostname>\S+?)?(:(?P<port>\d+))?/(?P<database>\S+)$'
    )

    def __init__(self, args):
        parsed = self.parser.parse_args(args)

        uri = self.uri_re.match(parsed.uri)
        if uri is None:
            # TODO: specify value format in error message
            raise ValueError('"%s" is not a valid postgres URI' % uri)
        params = uri.groupdict()

        self.conn = connect(
            database=params['database'],
            user=params['user'],
            password=params['password'],
            host=params['hostname'] or 'localhost',
            port=int(params['port'] or '5432'),
        )

        # stopped should be True if a migration raises an error
        self.stopped = False

    def _create_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trek_migrations (
                    name TEXT PRIMARY KEY
                )
            ''')

        self.conn.commit()


    def version(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                    SELECT name FROM trek_migrations
                    ORDER BY name DESC
                    LIMIT 1
                ''')
                result = cursor.fetchone()

            self.conn.commit()

        except ProgrammingError as err:
            if 'relation "trek_migrations" does not exist' in str(err):
                self.conn.rollback()
                self._create_table()
            else:
                raise

            return self.version()
        finally:
            cursor.close()

        return result[0] if result is not None else result

    def _split_sql(self, sql):
        return [
            stmt for stmt in sql.split(';')
            if stmt.strip() != ''
        ]

    def up(self, name, migration):
        if self.stopped:
            yield 'info', 'Already stopped.'

        try:
            with self.conn.cursor() as cursor:
                map(cursor.execute, self._split_sql(migration.up))
                cursor.execute(
                    "INSERT INTO trek_migrations VALUES (%s)",
                    (name,)
                )

            self.conn.commit()

            yield 'info', 'Migrated %s up' % (name)
        except ProgrammingError as err:
            self.stopped = True
            yield 'error', 'Migrating %s up resulted in an error: %s' % (name, err)

    def down(self, name, migration):
        if self.stopped:
            yield 'info', 'Already stopped.'

        try:
            with self.conn.cursor() as cursor:
                map(cursor.execute, self._split_sql(migration.down))
                cursor.execute(
                    "DELETE FROM trek_migrations WHERE name = %s",
                    (name,)
                )

            self.conn.commit()

            yield 'info', 'Migrated %s down' % (name)
        except ProgrammingError as err:
            self.stopped = True
            yield 'error', 'Migrating %s down resulted in an error: %s' % (name, err)
