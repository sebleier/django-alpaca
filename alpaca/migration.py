"""
The FixtureMigration class is a subclass of South's DataMigration class.  It
helps fascilitate the loading and removing of fixture data as migrations are
run forwards and backwards.

One of the icky design decisions I had to make was whether or not it was
necessary to monkey patch a function within django, specifically _get_model
from from django.core.serializers.python.  _get_model is used by Django's
deserializer to get the model class based on a "app_label.model" string.
However, since we may require the frozen orm, be need to return the frozen
model class.

An alternate to monkey patching would be to copy the python serializer code
from Django, modify it using the frozen model getter, and then unregister/
register the new deserializer.  Both seem icky, so the monkey patching was
chosen, since it is less complex and reduces the amount of code.
"""


import os

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.serializers import base
from django.core.serializers.python import _get_model
from django.db import transaction
from django.utils.importlib import import_module

from alpaca.loaders import PoliteLoader
from alpaca.removers import OverwriteRemover

from south.v2 import DataMigration


def _get_frozen_model(model_identifier):
    """
    Helper to look up a model from an "app_label.module_name" string.
    """
    try:
        Model = _get_frozen_model.orm[model_identifier]
    except TypeError:
        Model = None
    if Model is None:
        raise base.DeserializationError(u"Invalid model identifier: '%s'" % model_identifier)
    return Model


class FixtureMigration(DataMigration):
    fixtures = None
    loader = DeferLoader
    remover = OverwriteRemover

    def __init__(self, *args, **kwargs):
        if self.fixtures is None:
            raise ValidationError('Must specify at least one fixture to load.')
        self.import_cache = {}
        self.loader_instance = self.loader()
        self.remover_instance = self.remover()
        return super(FixtureMigration, self).__init__(*args, **kwargs)

    def save_obj(self, obj):
        self.loader_instance.save_obj(obj)

    def remove_obj(self, obj):
        self.remover_instance.remove_obj(obj)

    def get_fixture_path(self, fixture):
        """
        Returns the absolute path for the fixture.

        ``fixture`` can be a file name, e.g. news.json.  This will look in the
        current app's fixtures directory for the file name.

        ``fixture`` can also be relative to imported modules.  For example,
        if fixture is "project/news/fixtures/news.json", project will be
        imported and used to calculate the absolute path.
        """
        parts = fixture.split("/")
        if len(parts) == 1:
            # find the installed app's module
            bits = self.__module__.split('.')
            while bits and ".".join(bits) not in settings.INSTALLED_APPS:
                bits = bits[:-1]
            if not bits:
                return None
            app_path = ".".join(bits)
            mod = self.import_cache.get(app_path, None)
            if mod is None:
                self.import_cache[app_path] = mod = import_module(app_path)
            path = os.path.join(mod.__path__[0], 'fixtures', parts[0])
        else:
            mod = self.import_cache.get(parts[0], None)
            if mod is None:
                self.import_cache[parts[0]] = mod = import_module(parts[0])
            path = os.path.join(mod.__path__[0], *parts[1:])
        if not os.path.isfile(path):
            return None
        return path

    def gather_objects(self):
        """Loads and returns all objects found within the fixtures."""
        objects = []
        for fixture_label in self.fixtures:
            parts = fixture_label.split('.')
            if len(parts) == 1:
                fixture_name = parts[0]
                formats = serializers.get_public_serializer_formats()
            else:
                fixture_name, format = '.'.join(parts[:-1]), parts[-1]
                if format in serializers.get_public_serializer_formats():
                    formats = [format]
                else:
                    formats = []
            if not formats:
                raise Exception("Problem installing fixture '%s': %s is not a known serialization format.\n" %
                    (fixture_name, format))
            full_path = self.get_fixture_path(fixture_label)
            try:
                fixture = open(full_path, 'r')
                objects.extend(serializers.deserialize(format, fixture))
            finally:
                fixture.close()
        return objects

    def monkey_patch(self):
        """Monkey patch _get_model.  Oops, God just killed a kitten"""
        self.old_get_model = _get_model
        _get_model = _get_frozen_model
        _get_model.orm = self.orm

    def unmonkey_patch(self):
        _get_model = self.old_get_model

    def process(self, action):
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        try:
            self.monkey_patch()
            objects = self.gather_objects()
            for obj in objects:
                action(obj)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            import traceback
            transaction.rollback()
            transaction.leave_transaction_management()
            traceback.print_exc()
            return
        finally:
            self.unmonkey_patch()

        transaction.commit()
        transaction.leave_transaction_management()

    def forwards(self, orm):
        self.orm = orm
        self.process(self.save_obj)

    def backwards(self, orm):
        self.orm = orm
        self.process(self.remove_obj)
