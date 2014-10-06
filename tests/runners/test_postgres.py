# -*- coding: utf-8 -*-
from trek.migration import Migration
from trek.runners.postgres import PostgresRunner
from psycopg2 import ProgrammingError
import pytest

TABLE_QUERY = '''
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
'''

TABLE = 'test1'
UP = 'CREATE TABLE %s (id INTEGER PRIMARY KEY)' % TABLE
DOWN = 'DROP TABLE %s' % TABLE

MIGRATION = Migration('-- MIGRATE UP\n%s\n-- MIGRATE DOWN\n%s' % (UP, DOWN))

def _create(connection):
    with connection.cursor() as cursor:
        cursor.execute(UP)
    connection.commit()

def _drop(connection):
    with connection.cursor() as cursor:
        try:
            cursor.execute(DOWN)
        except ProgrammingError as err:
            connection.rollback()
            if 'table "%s" does not exist' % TABLE in str(err):
                return
            else:
                raise

    connection.commit()

def _table_presence(connection, tablename, present):
    with connection.cursor() as cursor:
        cursor.execute(TABLE_QUERY)

        if present:
            assert (tablename,) in cursor.fetchall()
        else:
            assert (tablename,) not in cursor.fetchall()

@pytest.yield_fixture
def runner(postgres_info, connection, cursor):
    runner = PostgresRunner(['postgres://%s%s@%s%s/%s' % (
        postgres_info['user'],
        ':' + postgres_info['password'] if postgres_info['password'] else '',
        postgres_info['host'],
        ':%d' % postgres_info['port'] if 'port' in postgres_info else '',
        postgres_info['database'],
    )])
    assert not runner.stopped

    yield runner

    cursor.execute('DROP TABLE IF EXISTS trek_migrations')
    connection.commit()


class TestVersion(object):
    def test_creates_table(self, connection, runner):
        _table_presence(connection, 'trek_migrations', False)

        assert runner.version() is None

        _table_presence(connection, 'trek_migrations', True)

    def test_returns_version(self, connection, runner):
        runner._create_table()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO trek_migrations VALUES ('1')")
        connection.commit()

        assert runner.version() == '1'


def test_up(request, connection, runner):
    runner._create_table()
    _table_presence(connection, TABLE, False)
    request.addfinalizer(lambda: _drop(connection))

    name = '1'
    messages = list(runner.up(name, MIGRATION))
    assert len(messages) == 1
    level, message = messages[0]

    assert level == 'info'
    assert message == 'Migrated 1 up'
    assert not runner.stopped

    with connection.cursor() as cursor:
        cursor.execute('SELECT name FROM trek_migrations')
        assert cursor.fetchall() == [(name,)]

    _table_presence(connection, TABLE, True)


def test_down(request, connection, runner):
    name = '1'
    runner._create_table()
    _create(connection)
    request.addfinalizer(lambda: _drop(connection))
    _table_presence(connection, TABLE, True)

    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO trek_migrations VALUES (%s)", (name,))
    connection.commit()

    messages = list(runner.down(name, MIGRATION))
    assert len(messages) == 1
    level, message = messages[0]

    assert level == 'info'
    assert message == 'Migrated 1 down'
    assert not runner.stopped

    with connection.cursor() as cursor:
        cursor.execute('SELECT name FROM trek_migrations')
        assert cursor.fetchall() == []

    _table_presence(connection, TABLE, False)
