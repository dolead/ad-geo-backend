#!/usr/bin/env python
from setuptools import setup, find_packages

REQUIREMENTS = ['pymongo>=2.8', 'python-slugify==1.2.6']


setup(name='ad-geo-backend',
      version='1.1.7',
      description='Geographical data management',
      url='https://github.com/dolead/ad-geo-backend',
      author_email='backend@dolead.com',
      install_requires=REQUIREMENTS,
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'load-geo-data = ad_geo_backend.shell:load',
          ],
      },
      )
