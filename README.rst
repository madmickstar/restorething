Restorething
============
``restorething`` is a tool for restoring files from a syncthing verisoning directory. Supply ``restorething`` the path to the syncthing versioning directory and a date, it will index the available files in the versioning directory and restore based on the date supplied.


Restore Modes
-------------
``restorething`` will restore files using the following modes

* Nearest file before a specific date/time
* Nearest file after a specific date/time
* Nearest file before/after a specific date/time

``restorething`` has filtering options

* Filter files with specific string
* Filter dir with specific string


Installation
-------------
``restorething`` from source

.. code:: bash

    $ python setup.py sdist
    $ pip install dist\restorething-x.x.x.tar.gz


``restorething`` from PyPI

.. code:: bash

    $ pip install restorething


Usage
-----
In all of the following cases, if no hour is supplied the default time value is set to 23:59:59.

Restore closest file before 6am 15th August 2016, if no file is found ``restorething`` will look for the closet file after 6am 15th August 2016.

.. code:: bash

    $ python -m restorething 20160815 -vd sync/.stversions -hr 6

Restore closest file after 6am 15th August 2016, if no file is found, no file will be restored.

.. code:: bash

    $ python -m restorething 20160815 -vd sync/.stversions -hr 6 -a

Restore closest file before 6am 15th August 2016, if no file is found, no file will be restored.

.. code:: bash

    $ python -m restorething 20160815 -vd sync/.stversions -hr 6 -b

Restore closest file no more than 10 hours before 6am 15th August 2016, if no file is found ``restorething`` will look for the closet file no more than 10 hours after 6am 15th August 2016.

.. code:: bash

    $ python -m restorething 20160815 -vd sync/.stversions -hr 6 -pm 10
