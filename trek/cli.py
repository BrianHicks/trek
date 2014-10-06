# -*- coding: utf-8 -*-
from argparse import ArgumentParser, REMAINDER
from . import Migrator, ALL
import sys


parser = ArgumentParser('migrate')
parser.add_argument(
    '-c', '--count',
    type=int, default=-1,
    help='how many migrations to migrate',
)
parser.add_argument(
    '-r', '--runner',
    type=str, default='migrate.shell:ShellMigrator',
    help='which migrator to run (specify Python path)',
)
parser.add_argument(
    '-d', '--directory',
    type=str, default='migrations',
    help='which diretory to look for migrations in',
)
parser.add_argument(
    'direction',
    type=str, choices=['up', 'down'],
    help='which direction to migrate'
)
parser.add_argument(
    'rest', nargs=REMAINDER,
)

migrators = {
    'postgres': 'migrate.runners.postgres:PostgresRunner'
}

def display_messages(messages):
    for level, message in messages:
        if level == 'raw':
            print message
        else:
            print '[%s]: %s' % (level, message)

def run():
    args = parser.parse_args()

    if args.runner in migrators:
        args.runner = migrators[args.runner]

    if args.count < 0:
        if args.direction == 'up':
            args.count = ALL
        else:
            args.count = 1

    migrator = Migrator(
        args.count,
        args.runner,
        args.directory,
        args.direction,
        args.rest
    )

    try:
        display_messages(migrator.run())
    except (OSError, ValueError) as err:
        print '[error]: %s' % err
        sys.exit(1)

    sys.exit(0)
