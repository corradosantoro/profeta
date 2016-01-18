#!/usr/bin/env python

from distutils.core import setup

setup(name='PROFETA',
      version='2.0',
      description='Python Robotic Framework',
      author='Corrado Santoro',
      author_email='santoro@dmi.unict.it',
      url='http://github.com/corradosantoro/profeta',
      packages=['profeta', 'profeta.clepta'],
      package_dir={'profeta': 'lib/profeta',
                   'profeta.clepta' : 'lib/profeta/clepta'}
)
