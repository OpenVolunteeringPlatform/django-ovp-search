# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ovp-search',
    version='0.1.1',
    author=u'Atados',
    author_email='arroyo@atados.com.br',
    packages=find_packages(),
    url='https://github.com/OpenVolunteeringPlatform/django-ovp-core',
    download_url = 'https://github.com/OpenVolunteeringPlatform/django-ovp-core/tarball/0.1.1',
    license='AGPL',
    description='This module has search functionality for' + \
                ' ovp projects and nonprofits',
    long_description=open('README.rst', encoding='utf-8').read(),
    zip_safe=False,
    install_requires = [
      'Django>=1.10.1,<1.11.0',
      'djangorestframework>=3.4.7,<3.5.0',
      'codecov>=2.0.5,<2.1.0',
      'coverage>=4.2,<4.3.0',
      'django-haystack>=2.5.0,<2.6.0',
      'ovp_projects>=0.1.0,<1.0.0',
    ]
)
