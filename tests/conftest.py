# -*- coding: utf-8 -*-
import pytest
import py
from migrate import Migrator

TEST_COMMENTS = ['#', '--', '//', ';', '"']

@pytest.fixture(params=TEST_COMMENTS)
def up_stmt(request):
    return '%s MIGRATE UP' % request.param

@pytest.fixture(params=TEST_COMMENTS)
def down_stmt(request):
    return '%s MIGRATE DOWN' % request.param


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
def migrator(request):
    marker = request.node.get_marker('migrator')
    opts = {} if marker is None else marker.kwargs

    temp_migrations_dir = py.path.local.mkdtemp()

    m = Migrator(
        count=opts.get('count', None),
        runner_path=opts.get('runner_path', DEBUG_RUNNER_PATH),
        migrations_dir=opts.get('migrations_dir', str(temp_migrations_dir)),
        direction=opts.get('direction', 'up'),
        extra=opts.get('extra', ['test'])
    )

    yield m

    temp_migrations_dir.remove()
