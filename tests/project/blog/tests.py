import glob
import os
from os.path import abspath, join, dirname
import shutil
import subprocess
import sys
from time import sleep
from django.conf import settings
from django.test import TestCase
import project
from project.blog.models import Entry, Blog

class AlpacaTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        self.do_cleanup = False
        self.base = dirname(abspath(project.__file__))
        super(AlpacaTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        settings.DATABASES['default']['NAME'] = 'project.db'
        self.assertEqual(settings.DATABASES['default']['NAME'], 'project.db')

    def tearDown(self):
        if self.do_cleanup:
            self.cleanup()

    def cleanup(self):
        for name in glob.glob(join(self.base, 'blog', 'migrations', '0*')):
            os.remove(name)
        os.remove(join(self.base, 'project.db'))

    def copy_models(self, template):
        shutil.copy(
            join(self.base, '..', 'code_templates', template),
            join(self.base, 'blog', 'models.py')
        )

    def call_command(self, command):
        setup_command = "export PYTHONPATH=`pwd`/..:`pwd`%s && " % ":".join(sys.path)
        print setup_command
        args = [setup_command, "python", "manage.py", command]
        retval = subprocess.call([" ".join(args)], shell=True, cwd=self.base)
        self.assertEqual(retval, 0)

    def test_a_initial_migration(self):
        self.call_command('syncdb --noinput')
        self.copy_models('blog_a.py')
        self.call_command('schemamigration blog --initial')

    def test_b_running_initial_migration(self):
        self.call_command('migrate blog')

    def test_c_add_field(self):
        self.copy_models('blog_b.py')
        self.call_command('schemamigration blog --auto')

    def test_d_add_fixture_migration(self):

        self.do_cleanup = True
        self.call_command('fixture_migration blog add_blog_data')
        #self.assertEqual(Blog.objects.count(), 0)
        #self.assertEqual(Entry.objects.count(), 0)
        self.call_command('migrate blog')
        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(Entry.objects.count(), 2)

