#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import re
import sys
import logging
import sqlite3
import time
import datetime


def process_db_mod_time(frz_time, database_file):
    logger = logging.getLogger(__name__)
    try:
        file_mod_time = round(os.stat(database_file).st_mtime)
        current_time = int(time.time())
    except:
        logger.error('Failed to Calc DB mod time')
        return True

    if (current_time - file_mod_time) > frz_time:
        logger.debug('(%s - %s) is greater than freeze period %s ', current_time, file_mod_time, frz_time)
        return True
    else:
        logger.debug('(%s - %s) is less than freeze period %s ', current_time, file_mod_time, frz_time)
        return False


def init_db(database_file):
    # Connect to DB file on disk
    logger = logging.getLogger(__name__)
    try:
        con = sqlite3.connect(database_file)
        con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
    except:
        print 'Error initialising, exiting...' + database_file
        logger.error('Could not initialise DB %s, exiting...', database_file)
        sys.exit(1)
    logger.info('Successfully initialised DB file %s', database_file)
    return con


def create_db(cur):
    # create tables
    logger = logging.getLogger(__name__)
    logger.info('Creating DB')

    # Creating a first table with first column as PRIMARY KEY
    cur.execute('''DROP TABLE IF EXISTS tb_dir_in ''')
    cur.execute('''CREATE TABLE tb_dir_in
           (id_dir        INTEGER PRIMARY KEY AUTOINCREMENT      NOT NULL,
            dir           TEXT    NOT NULL,
            dir_orig      TEXT    NOT NULL);''')
    logger.info('Created table dir in')

    # Creating a second table which references first table PRIMARY KEY
    cur.execute('''DROP TABLE IF EXISTS tb_file_out ''')
    cur.execute('''CREATE TABLE tb_file_out
           (id_file_out    INTEGER PRIMARY KEY AUTOINCREMENT      NOT NULL,
            id_dir         INT     NOT NULL,
            filename_out   TEXT    NOT NULL,
            conflict_flag  INT     NOT NULL,
            delete_flag    INT     NOT NULL);''')
    logger.info('Created table file out')

    # Creating a third table which references first table PRIMARY KEY
    cur.execute('''DROP TABLE IF EXISTS tb_file_in ''')
    cur.execute('''CREATE TABLE tb_file_in
           (id_file_in     INTEGER PRIMARY KEY AUTOINCREMENT      NOT NULL,
            id_file_out    INT     NOT NULL,
            filename_in    TEXT    NOT NULL,
            date           TEXT    NOT NULL,
            time           TEXT    NOT NULL,
            epoch          INT     NOT NULL);''')
    logger.info('Created table file in')


def strip_file_date_time(file):
    # strip date time from file and return filename
    # expecting file format filename~20160101-112011.ext
    # if no file date to remove return file as is
    logger = logging.getLogger(__name__)
    try:
        regex = re.compile(r'~\d{8}-\d{6}\.', re.I)
        file_nodate = regex.sub(r'.', file)
    except:
        file_nodate = file
    logger.debug('Removing date from filename %s returning filename %s', file, file_nodate)
    return file_nodate


def get_file_date_time(root, file):
    # matches first 8 digits but must be proceeded by ~ and followed by - and 6 digits and a .
    # matches last 6 digits but must be proceeded by 8 digits then a -, and followed by a .
    # grouped into two groups and it uses group 1
    logger = logging.getLogger(__name__)
    try:
        d = re.search(r'((?<=~)\d{8})(-\d{6}\.)', file)
        f_date = d.group(1)
        t = re.search(r'((?<=~\d{8}-)\d{6})(\.)', file)
        f_time = t.group(1)
        logger.debug('Detected syncthing backup file %s date %s time %s', file, str(f_date), str(f_time))
    except:
        # get file mod date time
        relative_file = os.path.join(root, file)
        f_date_time = int(os.path.getmtime(relative_file))
        f_date = datetime.datetime.fromtimestamp(f_date_time).strftime('%Y%m%d')
        f_time = datetime.datetime.fromtimestamp(f_date_time).strftime('%H%M%S')
        #print 'not a syncthing backup file', f_date, f_time
    return f_date, f_time


def check_file_conflict(file):
    # confirm its a conflict file
    if re.search(r'\.sync-conflict-\d{8}-\d{6}', file, re.I) is not None:
        return True
    else:
        return False


def remove_versioning_dir_from_path(root):
    # remove .stversions or .stversions/ from root
    try:
        regex = re.compile(r'\.stversions[\/\\]?', re.I)
        dir = regex.sub('', root)
    except:
        dir = root
    return dir


def check_file_exists(relative_file):
    # expects filename encoded the same as OS - UTF-8 encoded probably
    try:
        if os.path.isfile(relative_file):
            return True
        else:
            return False
    except:
        return False


def insert_table_dir_in(cur, root, orig_src_path):
    cur.execute('''INSERT INTO tb_dir_in (dir,dir_orig) \
          VALUES (?, ?)''', (root, orig_src_path));
    # return last ID
    return cur.lastrowid


def insert_table_file_out(cur, id_root, file_nodate, conflicted_flag, deleted_flag):
    cur.execute('''INSERT INTO tb_file_out (id_dir,filename_out,conflict_flag,delete_flag) \
          VALUES (?, ?, ?, ?)''', (id_root, file_nodate, conflicted_flag, deleted_flag));
    # return last ID
    return cur.lastrowid


def insert_table_file_in(cur, id_fo, file, date, time, epoch):
    # add file details
    cur.execute('''INSERT INTO tb_file_in (id_file_out,filename_in,date,time,epoch) \
          VALUES (?, ?, ?, ?, ?)''', (id_fo, file, date, time, epoch));


def update_last_variables(id_root, id_fo, root, file_nodate):
    # move variables into a tuple
    last_variables = [id_root, id_fo, root, file_nodate]
    return last_variables
