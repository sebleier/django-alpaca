#!/usr/bin/env python
import sys
import os
from os.path import dirname, abspath, join


def prep_environment():
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    sys.path.insert(0, join(parent, '..'))
    if not os.environ.get('DJANGO_SETTINGS_MODULE', None):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'


def runtests(*test_args):
    if not test_args:
        test_args = ['blog']

    runner = DjangoTestSuiteRunner(verbosity=1, interactive=True, failfast=False)
    failures = runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    prep_environment()
    from django.test.simple import DjangoTestSuiteRunner
    runtests(*sys.argv[1:])
