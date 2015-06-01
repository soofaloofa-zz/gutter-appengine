import os
import sys
import unittest
from invoke import task, run

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


@task
def flake8():
    """
    Run flake8.
    """
    run("flake8")


@task
def fetch_deps():
    """
    Fetch dependencies and install to ./vendor.
    """
    run("pip install -r requirements.txt -t vendor")


@task
def publish(repository=None):
    """
    Publish a new version to PyPI.
    Requires configuring ~/.pypirc with valid credentials.
    """
    if repository:
        run("python setup.py sdist upload -r %s" % repository)
    else:
        run("python setup.py sdist upload")


@task
def test():
    """
    Run tests.
    """
    if not os.path.isdir('./vendor'):
        fetch_deps()

    sys.path.append(os.environ['GAE_SDK_ROOT'])
    sys.path.append('./gutter/')
    sys.path.append('./vendor/')

    import dev_appserver
    dev_appserver.fix_sys_path()

    suite = unittest.loader.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(suite)
