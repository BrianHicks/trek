Migrate
=======

Migrate is a *simple* tool to do migrations of whatever you'd like. It has
terrible documentation because it's pre-1.0.

Usage
-----

Install! ``pip install migrate``

Now say you have a directory of migrations::

    migrations
    ├── 1.sql
    ├── 2.sql
    └── 3.sql

Where each of these looks a bit like this::

    -- MIGRATE UP
    CREATE TABLE test (
        id INTEGER PRIMARY KEY
    );

    -- MIGRATE DOWN
    DROP TABLE test;

(using any comment character, but lines with ``MIGRATE UP`` and ``MIGRATE
DOWN`` will be excluded and only one of each line is expected. Also note that
to simplify this example the numbers have been used, but you should probably
use timestamps like ``2014-01-01T00-00-00_human_name.sql``)

You can then run::

    migrate --runner=postgres up postgres://migrate_test@localhost/migrate_test

And the migrations will be run for you. Magic!

Writing your own runner
-----------------------

A runner is just a Python object with ``version``, ``up``, and ``down``
methods. ``version`` will be called with no arguments to determine the current
version, while ``up`` and ``down`` will be called with a name (string) and
``Migration`` object (which has string ``up`` and ``down`` members). ``up`` and
``down`` should be generators, and you can yield as many messages as you need
to so that the user knows what's going on.

After you put your migrator in a file, specify it with
``python.path.to.module:MigratorName``. For example, the postgres migrator is
expanded by the CLI interface but it's full path is
``migrate.runners.postgres:PostgresRunner``

TODO
----

- ✓ release on PyPI
- ✓ add Postgres migrator
- add other migrators as needed (open an issue on Github, for what you want,
  please!)
- add flask-script manager interface
