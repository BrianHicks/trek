# -*- coding: utf-8 -*-
import pytest
from migrate import migration


class TestMigration(object):
    up = 'CREATE DATABASE test;'
    down = 'DROP DATABASE test;'

    @pytest.mark.parametrize('how', ['up', 'down'])
    @pytest.mark.parametrize('lines', [0, 1, 2])
    def test_normal(self, how, lines, up_stmt, down_stmt):
        up = '\n'.join([self.up] * lines)
        down = '\n'.join([self.down] * lines)

        mig = migration.Migration('\n'.join([
            up_stmt,   up,
            down_stmt, down,
        ]))

        if how == 'up':
            assert mig.up == up
        if how == 'down':
            assert mig.down == down

    @pytest.mark.parametrize('count', [0, 2])
    @pytest.mark.parametrize('how', ['up', 'down'])
    def test_invalid(self, count, how, up_stmt, down_stmt):
        lines = []
        lines += [up_stmt] * (count if how == 'up' else 1) + [self.up]
        lines += [down_stmt] * (count if how == 'down' else 1) + [self.down]

        with pytest.raises(ValueError) as err:
            migration.Migration('\n'.join(lines))

        msg = 'Need exactly one %s migration, have %d' % (how, count)
        assert msg in str(err)
