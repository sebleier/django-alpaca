"""
Data migration creation command
"""

import sys
import os
import re
from optparse import make_option

try:
    set
except NameError:
    from sets import Set as set

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import models
from django.conf import settings
from south.management.commands.datamigration import Command as DataMigrationCommand
from south.migration import Migrations
from south.exceptions import NoMigrations
from south.creator import freezer

class Command(DataMigrationCommand):
    option_list = BaseCommand.option_list + (
        make_option('--freeze', action='append', dest='freeze_list', type='string',
            help='Freeze the specified app(s). Provide an app name with each; use the option multiple times for multiple apps'),
        make_option('--stdout', action='store_true', dest='stdout', default=False,
            help='Print the migration to stdout instead of writing it to a file.'),
        #make_option('--fixture', action='append', dest='fixture_list', type='string',
        #    help='Fixture to use for the fixture migration'),
    )
    help = "Creates a new template data migration for the given app"
    usage_str = "Usage: ./manage.py fixture_migration appname [fixture.json]"

    def handle(self, app=None, name="", freeze_list=None, stdout=False, verbosity=1, **options):
        # Any supposed lists that are None become empty lists
        freeze_list = freeze_list or []
        fixtures = options.get('fixtures', ['blogs.json'])
        # --stdout means name = -
        if options.get('stdout', None):
            name = "-"

        # Only allow valid names
        if re.search('[^_\w]', name) and name != "-":
            self.error("Migration names should contain only alphanumeric characters and underscores.")

        # if not name, there's an error
        if not name:
            self.error("You must provide a name for this migration\n" + self.usage_str)

        if not app:
            self.error("You must provide an app to create a migration for.\n" + self.usage_str)

        # Get the Migrations for this app (creating the migrations dir if needed)
        migrations = Migrations(app, force_creation=True, verbose_creation=verbosity > 0)

        # See what filename is next in line. We assume they use numbers.
        new_filename = migrations.next_filename(name)

        # Work out which apps to freeze
        apps_to_freeze = self.calc_frozen_apps(migrations, freeze_list)

        # So, what's in this file, then?
        file_contents = MIGRATION_TEMPLATE % {
            "fixutres": ",".join(fixtures),
            "frozen_models":  freezer.freeze_apps_to_string(apps_to_freeze),
            "complete_apps": apps_to_freeze and "complete_apps = [%s]" % (", ".join(map(repr, apps_to_freeze))) or ""
        }

        # - is a special name which means 'print to stdout'
        if name == "-":
            print file_contents
        # Write the migration file if the name isn't -
        else:
            fp = open(os.path.join(migrations.migrations_dir(), new_filename), "w")
            fp.write(file_contents)
            fp.close()
            print >>sys.stderr, "Created %s." % new_filename


MIGRATION_TEMPLATE = """# encoding: utf-8
import datetime
from alpaca.migration import FixtureMigration
from django.db import models
from south.db import db


class Migration(FixtureMigration):
    fixtures = [%(fixtures)s]

    models = %(frozen_models)s

    %(complete_apps)s
"""
