#!/usr/bin/env python

from distutils.core import setup


setup(name='Pyquake',
      version='1.0',
      entry_points={
          'console_scripts': [
          ]
      },
      description='Python Quake client',
      install_requires=['numpy', 'scipy'],
      author='Matt Earl',
      packages=['pyquake'])
