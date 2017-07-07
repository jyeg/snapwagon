# Standard library imports.
import os

# Django imports.
import django
from django.conf import settings
from django.test.utils import get_runner

__author__ = 'Jason Parent'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TestRunner = get_runner(settings)


def run_tests():
    django.setup()
    test_runner = TestRunner()
    failures = test_runner.run_tests(['organizations.tests.test_apis'])
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    run_tests()
