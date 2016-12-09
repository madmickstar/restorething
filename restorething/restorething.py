#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re
import sys
import time

import rtlog
import rttools
import dbindex
import dbrestore

import logging
import logging.config
import logging.handlers
import ConfigParser

import argparse                                # import cli argument
from argparse import RawTextHelpFormatter      # Formatting help

'''
To do list
Recover all versions of a single file - must keep date and time in filename
'''

def process_cli():
    logger = logging.getLogger(__name__)
    
    # processes cli arguments and usage guide
    parser = argparse.ArgumentParser(prog='restorething',
                    description='''Restore tool for syncthing''',
                    epilog='''Command line examples \n\n \
                    POSIX Users \n \
                    python -m restorething 20160815 -vd sync/.stversions -hr 6 \n \
                    python -m restorething 20160815 -vd sync/.stversions -hr 6 -a \n \
                    python -m restorething 20160815 -vd sync/.stversions -hr 6 -b \n \
                    python -m restorething 20160815 -vd sync/.stversions -hr 6 -pm 10 -ns -rd test \n \
                     \n \
                    Windows Users \n \
                    python -m restorething 20160815 -vd sync\\.stversions -hr 6 \n \
                    python -m restorething 20160815 -vd sync\\.stversions -hr 6 -a \n \
                    python -m restorething 20160815 -vd sync\\.stversions -hr 6 -b \n \
                    python -m restorething 20160815 -vd sync\\.stversions -hr 6 -pm 10 -ns -rd test''',
                    formatter_class=RawTextHelpFormatter)
    g1 = parser.add_mutually_exclusive_group()
    g2 = parser.add_mutually_exclusive_group()
    parser.add_argument('date',
                        type=int,
                        metavar=('date {YYYYMMDD}'),
                        help='Date to restore files, date will be used to find closest file before or after date')
    parser.add_argument('-hr', '--hour',
                        default='0',
                        type=int,
                        choices=range(0, 24),
                        metavar=('[0..24]'),
                        help='Hour to restore files, time will be used to find closest file before or after time - Default=0, 0 = 23:59, 15 = 15:00, 2 = 2:00')
    g1.add_argument('-pm', '--plus-minus',
                        default='0',
                        type=int,
                        metavar=('[int]'),
                        help='Limit restore date/time plus/minus hours for desired date/time default=0, 0 = disabled, 2 = +/- 2 hour')
    g1.add_argument('-b', '--before',
                        action="store_true",
                        help='Restore files before desired date/time only - Default = disabled')
    g1.add_argument('-a', '--after',
                        action="store_true",
                        help='Restore files after desired date/time only - Default = disabled')
    parser.add_argument('-vd', '--versions-dir',
                        default='.stversions',
                        type=str,
                        metavar=('[dir]'),
                        help='Versioning directory to walk, default = .stversions')
    parser.add_argument('-dd', '--db-dir',
                        default='./',
                        type=str,
                        metavar=('[dir path]'),
                        help='Directory to find DB file, default = ./')
    parser.add_argument('-df', '--db-file',
                        default='st_restore.sqlite',
                        type=str,
                        metavar=('[file path]'),
                        help='DB file name, default = st_restore.sqlite')
    parser.add_argument('-nf', '--no-freeze',
                        action="store_true",
                        help='No 24hr DB freeze, default = disabled')
    parser.add_argument('-nd', '--no-delete',
                        action="store_true",
                        help='No deleted or renamed files in restore, default = disabled')
    parser.add_argument('-ic', '--inc-conflict',
                        action="store_true",
                        help='Inc conflict files in restore, default = disabled')
    g2.add_argument('-ff', '--filter-file',
                        default=None,
                        type=str,
                        metavar=('[string]'),
                        help='Filter out specific file name, default = No filtering')
    g2.add_argument('-fd','--filter-dir',
                        default=None,
                        type=str,
                        metavar=('[string]'),
                        help='Filter specific DIR, default = No filter')
    parser.add_argument('-ns','--no-sim',
                        action="store_true",
                        help='No simulate, restore for real, default = disabled')
    parser.add_argument('-rd','--restore-dir',
                        default='restore',
                        type=str,
                        metavar=('[dir path]'),
                        help='Restore DIR, default = restore')
    parser.add_argument('-d', '--debug',
                        action="store_true",
                        help='Enable program flow debug to console')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s v0.1.0')

    args = parser.parse_args()
    logger.debug('CLI Arguments %s', args)
    return args


def main():
    '''
    The main entry point of the application
    '''

    # process arguments from warnuser
    args = process_cli()

    # load the logging configuration
    logging_file = rtlog.main(args)
    try:
        logging.config.fileConfig(logging_file, disable_existing_loggers=False)
    except Exception, err:
        sys.stderr.write('ERROR: log config file - %s' % str(err))
        sys.exit(1)
        
    logger = logging.getLogger(__name__)
    
    logger.debug('CLI Arguments %s', args)
        
    d = rttools.validate_cli_date(args.date)
    h = rttools.process_cli_time(args.hour)
    try:
        cli_epoch = rttools.get_epoch(d, h)
    except Exception, err:
        sys.stderr.write('ERROR: %s' % str(err))
        return 1

    # check write permissions
    rttools.permissions(args)
    
    abs_path = rttools.convert_to_abspath(args.restore_dir, 'Restore DIR')
    
    # test restore dir path for .stfolder or .stversions    
    if rttools.restoredir_check(abs_path, '.stfolder'):
        rttools.warnuser()
    elif rttools.restoredir_check(abs_path, '.stversions'):
        rttools.warnuser()
    else:
        logger.debug('Restoring files to non syncthing operational dir')

    # Index the files
    dbindex.main(args.db_file, args.no_freeze, args.versions_dir)

    # Restore files from archive
    dbrestore.main(cli_epoch, abs_path, args)


if __name__ == "__main__":
    main()
