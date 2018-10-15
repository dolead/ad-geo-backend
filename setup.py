#!/usr/bin/env python
from setuptools import setup, find_packages

REQUIREMENTS = []

try:
    from pipenv.project import Project
    from pipenv.utils import convert_deps_to_pip
    pfile = Project(chdir=False).parsed_pipfile
    requirements = convert_deps_to_pip(pfile['packages'], r=False)
except ImportError:
    requirements = ['pymongo==2.8', 'python-slugify==1.2.6']


setup(name='ad-geo-backend',
      version='1.0.0',
      description='Geographical data management',
      url='https://github.com/dolead/ad-geo-backend',
      author_email='backend@dolead.com',
      install_requires=requirements,
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'load-geo-data = ad_geo_backend.shell:load',
          ],
      },
)
