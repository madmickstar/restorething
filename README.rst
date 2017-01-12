Restorething
============

``restorething`` is a tool for restoring files from a syncthing
verisoning archive. Supply ``restorething`` the path to the syncthing
versioning directory and a date, it will index the available files in
the versioning archive and restore files for you.

``restorething`` has multiple restore modes and the ability to filter
files and directories.

Restore Modes
-------------

``restorething`` will restore files using the following modes

-  Nearest file before/after a specific date/time (default behaviour)
-  Nearest file before a specific date/time
-  Nearest file after a specific date/time
-  All instances of a specific file with no date/time restriction

``restorething`` has filtering options

-  Filter files with specific string
-  Filter dir with specific string
-  Filter both dir and file with specific string

Installation
------------

``restorething`` from source

.. code:: bash

    $ python setup.py sdist
    $ pip install dist\restorething-x.x.x.tar.gz

``restorething`` from PyPI

.. code:: bash

    $ pip install restorething

Usage
-----

``$ python -m restorething { date [ -hr {0-24} | -b | -a | -pm {int} | -ai {path and filename} | -vd {dir} | -rd {dir} | -dd {dir} | -df {filename} | -nf | -nd | -ic | -ns | [ -ff {string} | -fd {string} | -fb {path and filename} ] | -d | --version] }``

+-----------+---------+---------------+--------------------------+-------------------+
| Argument  | Type    | Format        | Default                  | Description       |
+===========+=========+===============+==========================+===================+
| date      | integer | YYYYMMDD      | No default value. Field  | Date to restore   |
|           |         |               | must be supplied by user | files, date will  |
|           |         |               |                          | be used to find   |
|           |         |               |                          | closest file      |
|           |         |               |                          | before or after   |
|           |         |               |                          | date              |
+-----------+---------+---------------+--------------------------+-------------------+
| -hr       | integer | -hr {0-24}    | 12                       | Hour to compare   |
|           |         |               |                          | file's            |
|           |         |               |                          | modification time |
+-----------+---------+---------------+--------------------------+-------------------+
| -b        | switch  | -b            | disabled                 | Limit restore of  |
|           |         |               |                          | files to before   |
|           |         |               |                          | the supplied date |
|           |         |               |                          | and hour          |
+-----------+---------+---------------+--------------------------+-------------------+
| -a        | switch  | -a            | disabled                 | Limit restore of  |
|           |         |               |                          | files to after    |
|           |         |               |                          | the supplied date |
|           |         |               |                          | and hour          |
+-----------+---------+---------------+--------------------------+-------------------+
| -pm       | integer | -pm           | 0                        | Limit restore of  |
|           |         | {0-2147483647 |                          | files to          |
|           |         | hrs}          |                          | plus/minus hours  |
|           |         |               |                          | each side of the  |
|           |         |               |                          | supplied date and |
|           |         |               |                          | hour              |
+-----------+---------+---------------+--------------------------+-------------------+
| -ai       | string  | -ai {absolute | disabled                 | Recovers all      |
|           |         | path of file} |                          | versions of a     |
|           |         |               |                          | file ignoring any |
|           |         |               |                          | date and times    |
|           |         |               |                          | specified         |
+-----------+---------+---------------+--------------------------+-------------------+
| -vd       | string  | -vd {absolute | .stversions              | Sets the location |
|           |         | or relative   |                          | of the syncthing  |
|           |         | path of DIR}  |                          | versioning        |
|           |         |               |                          | folder, by        |
|           |         |               |                          | default script    |
|           |         |               |                          | looks in          |
|           |         |               |                          | directory script  |
|           |         |               |                          | is run from       |
+-----------+---------+---------------+--------------------------+-------------------+
| -rd       | string  | -rd {absolute | restore                  | Enables the       |
|           |         | or relative   |                          | ability to        |
|           |         | path of DIR}  |                          | restore to a      |
|           |         |               |                          | location other    |
|           |         |               |                          | than the default  |
+-----------+---------+---------------+--------------------------+-------------------+
| -dd       | string  | -dd {absolute | /home/name/.restorething | Enables the       |
|           |         | or relative   |                          | ability to use a  |
|           |         | path of DIR}  |                          | database file in  |
|           |         |               |                          | a different       |
|           |         |               |                          | location, default |
|           |         |               |                          | behaviour is to   |
|           |         |               |                          | store database    |
|           |         |               |                          | file in users     |
|           |         |               |                          | home directory    |
+-----------+---------+---------------+--------------------------+-------------------+
| -df       | string  | -df           | restorething.db          | Enables the       |
|           |         | {filename}    |                          | ability to use a  |
|           |         |               |                          | database file     |
|           |         |               |                          | with a different  |
|           |         |               |                          | name              |
+-----------+---------+---------------+--------------------------+-------------------+
| -nf       | switch  | -nf           | disabled                 | Enables indexing  |
|           |         |               |                          | archived files    |
|           |         |               |                          | every time script |
|           |         |               |                          | is run, by        |
|           |         |               |                          | default script    |
|           |         |               |                          | will reuse        |
|           |         |               |                          | existing DB file  |
|           |         |               |                          | for 24 hours      |
+-----------+---------+---------------+--------------------------+-------------------+
| -nd       | switch  | -nd           | disabled                 | Enables restoring |
|           |         |               |                          | files that have   |
|           |         |               |                          | been deleted or   |
|           |         |               |                          | changed due to    |
|           |         |               |                          | renaming, by      |
|           |         |               |                          | default deleted   |
|           |         |               |                          | or renamed files  |
|           |         |               |                          | are not included  |
|           |         |               |                          | in restore        |
+-----------+---------+---------------+--------------------------+-------------------+
| -ic       | switch  | -ic           | disabled                 | Enables restoring |
|           |         |               |                          | files that were   |
|           |         |               |                          | marked as         |
|           |         |               |                          | conflict files by |
|           |         |               |                          | syncthing and     |
|           |         |               |                          | deleted by user,  |
|           |         |               |                          | by default        |
|           |         |               |                          | conflict files    |
|           |         |               |                          | are not restored  |
+-----------+---------+---------------+--------------------------+-------------------+
| -ns       | switch  | -ns           | disabled                 | Enables no        |
|           |         |               |                          | simultation mode, |
|           |         |               |                          | default behaviour |
|           |         |               |                          | is to simulate    |
|           |         |               |                          | restore, no       |
|           |         |               |                          | simultation mode  |
|           |         |               |                          | will copy files   |
|           |         |               |                          | from syncthing    |
|           |         |               |                          | archive to hard   |
|           |         |               |                          | drive             |
+-----------+---------+---------------+--------------------------+-------------------+
| -ff       | string  | -ff {string}  | disabled                 | Recovers a single |
|           |         |               |                          | version of any    |
|           |         |               |                          | files matching    |
|           |         |               |                          | the string        |
|           |         |               |                          | supplied          |
+-----------+---------+---------------+--------------------------+-------------------+
| -fd       | string  | -fd {string}  | disabled                 | Recovers a single |
|           |         |               |                          | version of all    |
|           |         |               |                          | files in any DIR  |
|           |         |               |                          | matching the      |
|           |         |               |                          | string supplied   |
+-----------+---------+---------------+--------------------------+-------------------+
| -fb       | string  | -fb {absolute | disabled                 | Recovers a single |
|           |         | path of file} |                          | version of a file |
|           |         |               |                          | matching the DIR  |
|           |         |               |                          | and Filename      |
+-----------+---------+---------------+--------------------------+-------------------+
| -d        | switch  | -d            | disabled                 | Enables debug     |
|           |         |               |                          | output to console |
+-----------+---------+---------------+--------------------------+-------------------+
| --version | switch  | --version     | disabled                 | Displays version  |
+-----------+---------+---------------+--------------------------+-------------------+

Default behaviour
-----------------

-  The default behaviour of the script is to look for the closest file
   older (before) than supplied date/time. If nothing is found, the
   script looks for the closest file younger (after) than supplied
   date/time. The default behaviour can be limited to plus/minus hours
   by supplying ``-pm {hours}`` argument or changed to only looking
   before or after supplied date/time by using the ``-b`` or ``-a``
   flags, respectively.
-  If no hour is supplied the default time value the script uses is
   12pm. This can be changed by using the ``-hr {0-24}`` argument
-  The script will always simulate a restore by default giving the user
   an opportunity to review any detected warnings. By supplying the -ns
   flag, the user can enable the no simulation mode and do an actual
   restore, no simulation, no undo.
-  The script will create a directory named restore in the diretory the
   scrpt is being called from and restore all files recursively inside
   of it
-  If no syncthing versioning directory is supplied, the default
   behaviour is to look in the directory the script is being called
   from.
-  All config, log and database files are stored in user's home
   directory under the directory named .restorething.

Examples
--------

Restore closest file before 6am 15th August 2016, if no file is found
restore closet file after 6am 15th August 2016. Due to not supplying
versioning directory, script will need to be called from directory
containing versioning directory

.. code:: bash

    $ python -m restorething 20160815 -hr 6

Restore closest file after 6am 15th August 2016, if no file is found, no
file will be restored. Versioning directory is supplied as a relative
path to where the script is being called from.

.. code:: bash

    $ python -m restorething 20160815 -hr 6 -a -vd sync/.stversions

Restore closest file before 6am 15th August 2016, if no file is found,
no file will be restored. Versioning directory is supplied as a relative
path to where the script is being called from.

.. code:: bash

    $ python -m restorething 20160815 -hr 6 -b -vd sync/.stversions

Restore closest file no more than 10 hours before 6am 15th August 2016,
if no file is found ``restorething`` will look for the closet file no
more than 10 hours after 6am 15th August 2016. Versioning directory is
supplied as a relative path to where the script is being called from.

.. code:: bash

    $ python -m restorething 20160815 -hr 6 -pm 10 -vd sync/.stversions

Restore all instances of a file located in directory
``/some/important/directory/``, named ``file.txt``. Current script
limitation is you have to supply a date, although it will be ignored.

.. code:: bash

    $ python -m restorething 20160815 -ai /some/important/directory/file.txt 
