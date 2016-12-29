===========
Change log
===========

v0.1.0
-----------
* Start project
* Update README

v0.1.1
-----------
* Update codeship badge
* Enable haystack
* Create project indexes
* ProjectListView

v0.1.2
-----------
* Upgrade django-rest-framework to 3.5.3
* Rename ProjectList resource to SearchResource

v0.1.3
-----------
* Upgrade ovp-projects to 1.0.0
* Fix license name on README

v1.0.0
-----------
* Rename SearchResource to ProjectSearchResource
* Implement NonprofitSearchResource
* Implement TiedModelRealtimeSignalProcessor
* Implement /country-cities/ route
* Implement test suite
* Optimize search queries
* Release as stable

v1.0.1
-----------
* Add 'name' filter to Project and Organization search
* Add 'published' filter to Project and Organization search

v1.0.2
-----------
* Fix requirements

v1.0.3
-----------
* Upgrade to django-ovp-core 1.0.11

v1.0.4
-----------
* Fix problems with 'name' filter on OrganizationSearchViewSet

v1.0.5[unreleased]
-----------
* Fix maps api language on tests(override settings.py definition)
* Use both "locality" and "administrative_area_level_2" as city indicator
* Test signals using "administrative_area_level_2" as filter instead of "locality"
