===============================
Recommendr
===============================

.. image:: https://badge.fury.io/py/recommendr.png
    :target: http://badge.fury.io/py/recommendr
    
.. image:: https://travis-ci.org/chrislawlor/recommendr.png?branch=master
        :target: https://travis-ci.org/chrislawlor/recommendr


Movie recommendation engine.

* Free software: BSD license
* Documentation: http://recommendr.rtfd.org.

Features
--------

* A Redis backend for storing movie and rating data.

* A simple user-based recommendations algorithm with swappable distance
  functions.

* Item-based recommendation algorithm in work.

* A demo command-line client.


Try it Out
----------

* Clone the repo::

	git clone git@github.com:chrislawlor/recommendr.git

* Create a python virtual environment with virtualenvwrapper::

	mkvirtualenv recommendr

* Install requirements::

	pip install -r requirements.txt

* Install recommendr::

	python setup.py install

* First, import some MovieLens data into Redis::

	python data/import_data.py

* Run the demo program::

	python demo.py


The demo program will ask you for ratings until you have rated 5 movies, then
it will give some recommendations. Recommendations should improve the more
times you run the demo program.


*NOTE*: If your Redis instance is somewhere other than ``locahost:6379``, set
the ``REDIS_HOST`` and ``REDIS_PORT`` environment variables. If you wish to use
a Redis DB other than 1, set ``REDIS_DB``.


Key Code Points
---------------

``recommendr.db``: Implements a Redis DB backend suitable for storing movie
and rating information

::
	
	recommendr.get_user_based_recommendations(reviewer_id, num=20, similarity=sim_distance)

returns the top recommendations for a given user. It defaults to using
Euclidean distance for the similiarity function, optionally pass
``recommendr.similarity.sim_pearson`` to use the Pearson Coefficient.


Test Suite
----------

I haz one:

::
	
	python setup.py test
