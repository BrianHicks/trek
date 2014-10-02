# -*- coding: utf-8 -*-
import itertools


class Migration(object):
    _up = 'MIGRATE UP'
    _down = 'MIGRATE DOWN'

    def _validate(self, content):
        """a migration should have *exactly* one up and down statement"""
        ups = content.count(self._up)
        if ups != 1:
            raise ValueError('Need exactly one up migration, have %d' % ups)

        downs = content.count(self._down)
        if downs != 1:
            raise ValueError('Need exactly one down migration, have %d' % downs)

    def _parse_up(self, content):
        upstart = list(itertools.dropwhile(
            lambda line: self._up not in line, content.split('\n')
        ))[1:]
        upcontent = itertools.takewhile(
            lambda line: self._down not in line, upstart
        )
        return '\n'.join(upcontent)

    def _parse_down(self, content):
        downstart = list(itertools.dropwhile(
            lambda line: self._down not in line, content.split('\n')
        ))[1:]
        return '\n'.join(downstart)

    def __init__(self, content):
        self._validate(content)
        self.up = self._parse_up(content)
        self.down = self._parse_down(content)
