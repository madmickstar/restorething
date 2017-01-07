Restorething
============
`restorething` is a tool for restoring files from a syncthing verisoning directory. Supply `restorething` the path to the syncthing versioning directory and a date, it will index the available files in the versioning directory and restore based on the date supplied.


Restore Modes
-------------
`restorething` will restore files using the following modes
* Nearest file before a specific date/time
* Nearest file after a specific date/time
* Nearest file before/after a specific date/time

`restorething` has filtering options
* Filter files with specific string
* Filter dir with specific string


Installation
-------------
```restorething``` from source

```bash
    $ python setup.py sdist
    $ pip install dist\restorething-x.x.x.tar.gz
```

```restorething``` from PyPI
```bash
$ pip install restorething
```


Usage
-----
In all of the following cases, if no hour is supplied the default time value is set to 12:00:00.

Restore closest file before 6am 15th August 2016, if no file is found `restorething` will look for the closet file after 6am 15th August 2016.
```bash
$ python -m restorething 20160815 -vd sync/.stversions -hr 6
```

Restore closest file after 6am 15th August 2016, if no file is found, no file will be restored.
```bash
$ python -m restorething 20160815 -vd sync/.stversions -hr 6 -a
```

Restore closest file before 6am 15th August 2016, if no file is found, no file will be restored.
```bash
$ python -m restorething 20160815 -vd sync/.stversions -hr 6 -b
```

Restore closest file no more than 10 hours before 6am 15th August 2016, if no file is found `restorething` will look for the closet file no more than 10 hours after 6am 15th August 2016.
```bash
$ python -m restorething 20160815 -vd sync/.stversions -hr 6 -pm 10
```

```bash
$ python -m restorething {date [ -hr {0-24} | -b | -a | -pm {int} | -vd {dir} | -rd {dir} | -dd {dir} | -df {filename} | -nf | -nd | -ic | -ns | [ -ff {string} | -fd {string} | -fb {path and filename} | -fa {path and filename}] | -d | --version]}
```

Argument | Type | Format | Default | Description
---------|------|--------|---------|------------
date | integer | YYYYMMDD |  | Date to restore files, date will be used to find closest file before or after date
-hr | integer | -hr {0-24} | 12 | Hour to compare file's modification time
-b | switch | -b | disabled | Limit restore of files to before the supplied date and hour
-a | switch | -a | disabled | Limit restore of files to after the supplied date and hour
-pm | integer | -pm {0-2147483647} | 0 | Limit restore of files to plus/minus hours each side of the supplied date and hour
-vd | string | -vd {absolute or relative path of DIR} | .stversions | Sets the location of the syncthing versioning folder, by default script looks in directory script is run from
-rd | string | -rd {absolute or relative path of DIR} | restore | Enables the ability to restore to a location other than the default
-dd | string | -dd {absolute or relative path of DIR} | \user\homedir\\.restorething | Enables the ability to use a database file in a different location, default behaviour is to store database file in users home directory
-df | string | -df {filename} | st_restore.sqlite | Enables the ability to use a database file with a different name
-nf | switch | -nf | disabled | Enables indexing archived files every time script is run, by default script will reuse existing DB file for 24 hours
-nd | switch | -nd | disabled | Enables restoring files that have been deleted or changed due to renaming, by default deleted or renamed files are not included in restore
-ic | switch | -ic | disabled | Enables restoring files that were marked as conflict files by syncthing and deleted by user, by default conflict files are not restored
-ns | switch | -ns | disabled | Enables no simultation mode, default behaviour is to simulate restore, no simultation mode will copy files from syncthing archive to hard drive
-ff | string | -ff {string} | disabled | Recovers a single version of any files matching the string supplied
-fd | string | -fd {string} | disabled | Recovers a single version of all files in any DIR matching the string supplied
-fb | string | -fb {absolute path of file} | disabled | Recovers a single version of a file matching the DIR and Filename
-fa | string | -fa {absolute path of file} | disabled | Recovers all versions of a file ignoring any date and times specified
-d | switch | -d | disabled | Enables debug output to console
--version | switch | --version | disabled | Displays version