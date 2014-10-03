# -*- coding: utf-8 -*-
import pytest
import py
from migrate import Migrator, ALL

TEST_COMMENTS = ['#', '--', '//', ';', '"']
UP_CMD = 'MIGRATE UP'
DOWN_CMD = 'MIGRATE DOWN'

@pytest.fixture(params=TEST_COMMENTS)
def up_stmt(request):
    return '%s %s' % (request.param, UP_CMD)

@pytest.fixture(params=TEST_COMMENTS)
def down_stmt(request):
    return '%s %s' % (request.param, DOWN_CMD)


class DebugRunner(object):
    def __init__(self, args):
        self.args = args
        self.ups = []
        self.downs = []

    def version(self):
        return ''

    def up(self, name, migration):
        self.ups.append((name, migration))

    def down(self, name, migration):
        self.downs.append((name, migration))

DEBUG_RUNNER_PATH = '%s:%s' % (__name__, DebugRunner.__name__)


@pytest.yield_fixture
def migrations(request):
    """\
    take a specified amount of migrations and have them available in a
    temporary directory for the migrator. The migrations come from the
    `pytest.mark.migrations` marker, and are expect to be a number of
    (name, (up, down)) tuples, as args.

    Example:

        @pytest.mark.migrations(
            ('1', ('CREATE DATABASE test;', 'DROP DATABASE test;')),
        )
        def test_thing(migrations):
            # do something with migrations dir
            pass
    """
    marker = request.node.get_marker('migrations')
    migrations = [] if marker is None else marker.args

    # we don't need to test all the variations of migration comments here, only
    # in the parser. If this requirement changes in the future, the statements
    # here should just use the up_stmt and down_stmt fixtures.
    up_cmd = '%s %s' % (TEST_COMMENTS[0], UP_CMD)
    down_cmd = '%s %s' % (TEST_COMMENTS[0], DOWN_CMD)

    migrations_dir = py.path.local.mkdtemp()

    for name, (up, down) in migrations:
        migration = '\n'.join([up_cmd, up, down_cmd, down])
        migrations_dir.join(name).write(migration)

    yield migrations_dir

    migrations_dir.remove()


@pytest.fixture
def migrator(request, migrations):
    marker = request.node.get_marker('migrator')
    opts = {} if marker is None else marker.kwargs

    return Migrator(
        count=opts.get('count', ALL),
        runner_path=opts.get('runner_path', DEBUG_RUNNER_PATH),
        migrations_dir=str(migrations),
        direction=opts.get('direction', 'up'),
        extra=opts.get('extra', ['test'])
    )
