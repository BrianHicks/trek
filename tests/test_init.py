# -*- coding: utf-8 -*-
from .conftest import DebugRunner, DEBUG_RUNNER_PATH
from migrate.migration import Migration
import pytest


class TestRunner(object):
    @pytest.mark.migrator(runner_path=DEBUG_RUNNER_PATH)
    def test_load(self, migrator):
        "the runner should be loaded and initialized at runtime"
        assert isinstance(migrator.runner, DebugRunner)

    @pytest.mark.migrator(runner_path=DEBUG_RUNNER_PATH, extra=['initialized'])
    def test_initialize(self, migrator):
        "the runner should be initialized with passed arguments"
        assert migrator.runner.args == ['initialized']


class TestMigrationsToRun(object):
    @pytest.mark.migrations(
        ('1', ('', '')),
    )
    @pytest.mark.migrator(direction='up')
    def test_gets_all_for_zero(self, migrator):
        migrator.current = ''

        assert migrator.migrations_to_run() == ['1']

    @pytest.mark.migrations(('1', ('', '')), ('2', ('', '')))
    @pytest.mark.migrator(direction='up')
    def test_gets_next_for_up(self, migrator):
        migrator.current = '1'
        assert migrator.migrations_to_run() == ['2']

    @pytest.mark.migrations(('1', ('', '')), ('2', ('', '')))
    @pytest.mark.migrator(direction='down')
    def test_includes_current_for_down(self, migrator):
        migrator.current = '2'
        assert migrator.migrations_to_run() == ['2', '1']

    @pytest.mark.migrations(('1', ('', '')), ('2', ('', '')))
    @pytest.mark.migrator(count=1)
    def test_limits_to_count(self, migrator):
        migrator.current = ''
        assert migrator.migrations_to_run() == ['1']

    @pytest.mark.migrations(('1', ('', '')))
    @pytest.mark.migrator(direction='sideways')
    def test_raises_error_for_bad_migration_direction(self, migrator):
        with pytest.raises(ValueError) as err:
            migrator.migrations_to_run()

        assert 'Unknown migration direction "sideways"' in str(err)

    @pytest.mark.migrator(direction='sideways')
    def test_raises_error_for_no_migrations(self, migrator):
        with pytest.raises(ValueError) as err:
            migrator.migrations_to_run()

        assert 'No migrations to run in' in str(err)


@pytest.mark.migrations(('1', ('', '')))
def test_get_migration(migrator):
    "only a cursory test here, as Migration is tested elsewhere"
    migration = migrator.get_migration('1')
    assert isinstance(migration, Migration)


@pytest.mark.migrations(('1', ('up', 'down')))
@pytest.mark.parametrize('direction', ['up', 'down'])
def test_migrate(migrator, direction):
    migrator.direction = direction

    assert list(migrator.migrate(['1'])) == [('info', direction)]


@pytest.mark.migrations(('1', ('up', 'down')))
@pytest.mark.parametrize('direction', ['up', 'down'])
def test_run(migrator, direction):
    migrator.direction = direction
    migrator.current = '0' if direction == 'up' else '1'

    assert list(migrator.run()) == [
        ('info', direction),
        ('info', 'Ran 1 migration(s)')
    ]
