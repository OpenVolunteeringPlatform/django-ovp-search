# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ovp-search',
    version='1.0.15',
    author=u'Atados',
    author_email='arroyo@atados.com.br',
    packages=find_packages(),
    url='https://github.com/OpenVolunteeringPlatform/django-ovp-search',
    download_url='https://github.com/OpenVolunteeringPlatform/django-ovp-search/tarball/1.0.15',
    license='AGPL',
    description='This module has search functionality for' + \
                ' ovp projects and nonprofits',
    long_description=open('README.rst', encoding='utf-8').read(),
    zip_safe=False,
    install_requires = [
      'Django>=1.10.1,<1.11.0',
      'djangorestframework>=3.5.3,<3.6.0',
      'codecov>=2.0.5,<2.1.0',
      'coverage>=4.2,<4.4.0',
      'django-haystack>=2.5.0,<2.7.0',
      'ovp-projects>=1.2.7,<1.1.0',
      'ovp-users>=1.1.7,<2.0.0',
      'ovp-core>=1.2.4,<2.0.0',
      'ovp-uploads>=1.0.0,<2.0.0',
      'ovp-organizations>=1.2.9,<2.0.0',
      'djangorestframework-jwt>=1.9.0,<2.0.0',
      'whoosh>=2.7.4,<2.8.0',
    ]
)
