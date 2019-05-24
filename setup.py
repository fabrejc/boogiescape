#! /usr/bin/env python3

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name = 'boogiescape',
      version = '1.0.3',
      description = 'Tool for adjusting spatial representations of agricultural landscapes for the OpenFLUID modelling platform',
      long_description = readme(),
      author = 'Jean-Christophe Fabre',
      author_email = 'jean-christophe.fabre@inra.fr',
      url = 'http://github.com/fabrejc/boogiescape',
      license = 'GPLv3',
      packages = ['boogiescape'],
      entry_points = {
          'console_scripts': [
              'boogiescape = boogiescape.__main__:main'
          ]
      },
      test_suite='tests',
      install_requires = [
        'argparse',
        'networkx',
        'pydot'
      ]
)