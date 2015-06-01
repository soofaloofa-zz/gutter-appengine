"""
gutter-appengine
"""
from setuptools import setup
import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'gutter/appengine', 'VERSION')) as f:
    version = f.read().strip()

setup(
    name="gutter-appengine",
    version=version,
    description="An AppEngine front-end to gutter.",
    url='https://github.com/soofaloofa/gutter-appengine',
    license='MIT',
    author='Kevin Sookocheff',
    author_email='kevin.sookocheff@gmail.com',
    packages=['gutter.appengine'],
    package_data={
        'gutter.appengine': ['VERSION' 'include.yaml',
                             'templates/*.html', 'static/img/*.gif',
                             'static/js/*.js'],
    },
    namespace_packages=['gutter'],
    install_requires=['wtforms', 'datastoredict'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
