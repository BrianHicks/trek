# -*- coding: utf-8 -*-
from .migration import Migration
from importlib import import_module
import os

class Migrator(object):
    def __init__(self, count, runner_path, migrations_dir, direction, extra):
        self.count = count
        self.migrations_dir = migrations_dir
        self.direction = direction

        runner_cls = self.get_runner(runner_path)
        self.runner = runner_cls(extra)
        self.current = self.runner.version()

    def get_runner(self, path):
        package, name = path.split(':', 1)
        return getattr(import_module(package), name)

    def migrations_to_run(self):
        try:
            names = names(os.listdir(self.migrations_dir))
        except OSError:  # explicitly raising this. Deal with it!
            raise

        if not names:
            raise ValueError('No migrations to run in %s' % self.migrations_dir)

        if self.direction == 'up':
            return [
                m for m in migrations
                if self.current < m
            ][:self.count]
        elif self.direction == 'down':
            return [
                m for m in reversed(migrations)
                if self.current >= m
            ][:self.count]
        else:
            raise ValueError('Unknown migration direction "%s"' % self.direction)

    def run(self):
        "put all the parts together"
        names = self.migrations_to_run()
        if not names:
            return {'message': 'No migrations necessary!'}

        for name in names:
            with open(os.path.join(self.migrations_dir, name), 'r'):
                migration = Migration(mig.read())

            if self.direction == 'up':
                self.runner.up(name, migration)
            elif self.direction == 'down':
                self.runner.down(name, migration)
            else:
                raise ValueError('Unknown migration direction "%s"' % self.direction)

        return {'message': 'Ran %d migrations' % len(names)}
