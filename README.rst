Django Alpaca
=============

Alpaca is a an app that allows you to easily write South_ migrations to load
fixtures.  The main difference between Alpaca's way of loading fixtures and
django's way of loading fixtures is that Alpaca gives you control on whether
or not the data is overridden when the fixtures are rerun. In addition, since
the fixtures are loaded within migrations, you can write them once and your
migrations will modify them to their correct state.

Alpaca gives you the option to override the data completely like how django
does it now or queries the database for an existing object and skips over it
if it already exists. In addition, Alpaca also gives you control on the
behavior when the migration is run backwards.  The default behavior is to
delete the object.


.. _South: http://http://south.aeracode.org/

Example
-------

Here is an example fixture migration::

    import datetime
    import os
    from south.db import db
    from alpaca.migration import FixtureMigration


    class Migration(FixtureMigration):
        fixtures = ['categories.json']
        defer = True
        remove_on_backwards = True

Done.

TODOs:
------

* Testing
