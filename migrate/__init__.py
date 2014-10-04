# -*- coding: utf-8 -*-
from .migration import Migration
from importlib import import_module
import os

# the way this is used in a slice means that if we want all the migrations we
# need to specify them as `None` (because `[1,2,3][:None] == [1,2,3]`). Since
# this is pretty confusing, it's specified in this name instead.
ALL = None


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

    def get_migration(self, name):
        with open(os.path.join(self.migrations_dir, name), 'r') as raw:
            return Migration(raw.read())

    def migrations_to_run(self):
        try:
            names = os.listdir(self.migrations_dir)
        except OSError:  # explicitly raising this. Deal with it!
            raise

        if not names:
            raise ValueError('No migrations to run in %s' % self.migrations_dir)

        if self.direction == 'up':
            return [
                name for name in names
                if self.current < name
            ][:self.count]
        elif self.direction == 'down':
            return [
                name for name in reversed(names)
                if self.current >= name
            ][:self.count]
        else:
            raise ValueError('Unknown migration direction "%s"' % self.direction)

    def migrate(self, names):
        if not names:
            yield 'info', 'No migrations necessary!'
            return

        for name in names:
            migration = self.get_migration(name)

            if self.direction == 'up':
                yield 'migration', self.runner.up(name, migration)
            elif self.direction == 'down':
                yield 'migration', self.runner.down(name, migration)
            else:
                raise ValueError(
                    'Unknown migration direction "%s"' % self.direction
                )

    def run(self):
        "put all the parts together"
        names = self.migrations_to_run()
        for pair in self.migrate(names):
            yield pair

        yield 'info', 'Ran %d migration(s)' % len(names)
