==========
OVP Search
==========

.. image:: https://app.codeship.com/projects/58b28a40-7d1d-0134-1441-32b74bfe7659/status?branch=master
.. image:: https://codecov.io/gh/OpenVolunteeringPlatform/django-ovp-search/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/OpenVolunteeringPlatform/django-ovp-search
.. image:: https://badge.fury.io/py/ovp-search.svg
  :target: https://badge.fury.io/py/ovp-search

This module implements core search functionality. It is responsible for searching projects and nonprofits.

Getting Started
---------------
Prerequisites
""""""""""""""
This module relies on django-haystack to do full-text search. It was implemented and tested on top of ElasticSearch but should work with any backend.

Installing
""""""""""""""
1. Install django-ovp-search::

    pip install ovp-search

2. Add it to `INSTALLED_APPS` on `settings.py`

3. Add `haystack` to `INSTALLED_APPS`

4. Set up haystack connection::

    HAYSTACK_CONNECTIONS = {
      'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://%s/' % (os.environ.get('HS_SEARCH_ENDPOINT', '127.0.0.1:9200')),
        'INDEX_NAME': 'atadosovp'
      },
    }


Forking
""""""""""""""
If you have your own OVP installation and want to fork this module
to implement custom features while still merging changes from upstream,
take a look at `django-git-submodules <https://github.com/leonardoarroyo/django-git-submodules>`_.

Testing
---------------
To test this module

::

  python ovp_searcb/tests/runtests.py

Contributing
---------------
Please read `CONTRIBUTING.md <https://github.com/OpenVolunteeringPlatform/django-ovp-search/blob/master/CONTRIBUTING.md>`_ for details on our code of conduct, and the process for submitting pull requests to us.

Versioning
---------------
We use `SemVer <http://semver.org/>`_ for versioning. For the versions available, see the `tags on this repository <https://github.com/OpenVolunteeringPlatform/django-ovp-search/tags>`_. 

License
---------------
This project is licensed under the GNU GPLv3 License see the `LICENSE.md <https://github.com/OpenVolunteeringPlatform/django-ovp-search/blob/master/LICENSE.md>`_ file for details
