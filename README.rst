======================
A Python statsd client
======================

statsd_ is a friendly front-end to Graphite_. This is a Python client
for the statsd daemon.

.. image:: https://github.com/jsocol/pystatsd/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/jsocol/pystatsd/actions/workflows/ci.yml
   :alt: Latest CI status

.. image:: https://img.shields.io/pypi/v/statsd.svg
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/statsd.svg
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/wheel/statsd.svg
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Wheel Status

:Code:          https://github.com/jsocol/pystatsd
:License:       MIT; see LICENSE file
:Issues:        https://github.com/jsocol/pystatsd/issues
:Documentation: https://statsd.readthedocs.io/

Quickly, to use:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.

You can also add a prefix to all your stats:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo')
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.

If your network is not stable, you can add retry (version>=4.0.2)

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo', send_retries=2)  # will try total 2 times (default is 1) when send data
    >>> c.incr('bar')


Installing
==========

The easiest way to install statsd is with pip!

You can install from PyPI::

    $ pip install statsd

Or GitHub::

    $ pip install -e git+https://github.com/jsocol/pystatsd#egg=statsd

Or from source::

    $ git clone https://github.com/jsocol/pystatsd
    $ cd pystatsd
    $ python setup.py install


Docs
====

There are lots of docs in the ``docs/`` directory and on ReadTheDocs_.


.. _statsd: https://github.com/etsy/statsd
.. _Graphite: https://graphite.readthedocs.io/
.. _ReadTheDocs: https://statsd.readthedocs.io/en/latest/index.html


Development
====

Build package by poetry::


    pip install poetry

    poetry config repositories.<repo-name> <repo-url>
    poetry config http-basic.<repo-name> <user-name> <password>

    poetry build
    poetry publish -r <repo-name>  # or with user and password
    poetry publish -r <repo-name> -u <user-name> -p <password>
