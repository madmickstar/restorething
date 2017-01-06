#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import logging
import datetime


def process_working_dir():
    # prep working dir in users home DIR
    home_dir = os.path.expanduser('~')
    working_dir = os.path.join(home_dir, '.restorething')

    if os.path.isdir(working_dir):
        if not check_write_dir(working_dir):
            sys.stderr.write('ERROR: Failed write access to logging folder %s, exiting....' % working_dir)
            sys.exit(1)
    else:
        if not os.path.isdir(home_dir):
            sys.stderr.write('ERROR: Failed to find HOME DIR %s, exiting....' % home_dir)
            sys.exit(1)
        else:
            if not check_write_dir(home_dir):
                sys.stderr.write('ERROR: Failed write access to HOME DIR %s, exiting....' % home_dir)
                sys.exit(1)
            else:
                # create logging dir
                try:
                    os.makedirs(working_dir)
                except:
                    sys.stderr.write('ERROR: Failed to create logging DIR %s, exiting....' % working_dir)
                    sys.exit(1)

    return working_dir


def validate_cli_date(date):
    # process date
    logger = logging.getLogger(__name__)
    cli_date = str(date)
    # year 1000-2999 followed by months with 31 days and then months with 30 days then feb with up to 28 days - 29 days is handled below
    prog = re.compile('[1-2]\d{3}(((0[13578]|1[02])(0[1-9]|[12]\d|3[01]))|((0[469]|11)(0[1-9]|[12]\d|30))|(02(0[1-9]|1\d|2[0-8])))')
    result = prog.match(cli_date)
    if result:
        return cli_date
    else:
        chars = re.compile('[1-2]\d{7}')
        month = re.compile('\d{4}((0[1-9])|(1[0-2]))\d{2}')
        feb = re.compile('[1-2]\d{3}0229')
        if not chars.match(cli_date):
            raise RuntimeError('Wrong date format %s, expecting 8 integers in format YYYYMMDD' % cli_date)
        elif not month.match(cli_date):
            raise RuntimeError('Wrong date %s, Month does not exist' % cli_date)
        elif feb.match(cli_date):
            cli_yr = cli_date[0:4]
            if (int(cli_yr) % 4 == 0):
                return cli_date
            else:
                raise RuntimeError('Wrong date %s, February did not have 29 days that year' % cli_date)
        else:
            raise RuntimeError('Wrong date %s, Incorrect amount of days for month' % cli_date)


def process_cli_time(hour):
    # process hour
    if hour == 0:
        hour = str(235959)
    elif hour <= 9:
        hour = '0' + str(hour) + '0000'
    else:
        hour = str(hour) + '0000'
    return hour


def get_epoch(f_date, f_time):
    # expects date and time in the following format 20160101 235400
    # returns time in GMT
    logger = logging.getLogger(__name__)

    f_yr = f_date[0:4]
    f_mth = f_date[4:6]
    f_dy = f_date[6:8]
    f_hr = f_time[0:2]
    f_min = f_time[2:4]
    f_sec = f_time[4:6]
    try:
        epoch = (datetime.datetime(int(f_yr),int(f_mth),int(f_dy),int(f_hr),int(f_min),int(f_sec)) - datetime.datetime(1970,1,1)).total_seconds()
    except ValueError as e:
        raise RuntimeError('Day is out of range for month %s' % f_date, f_yr, f_mth, f_dy, ' exiting... Reason: %s' % e)
    except Exception as e:
        raise RuntimeError('Error processing epoch date %s' % f_date, f_yr, f_mth, f_dy, ' exiting... Reason: %s' % e)
    # covert time to local format
    epoch_local = int(time.mktime(time.gmtime(epoch)))
    logger.debug('Returning epoch in local time %s %s %s', f_date, f_time, epoch_local)
    return epoch_local


def check_write_dir(test_dir):
    if not os.access(test_dir, os.W_OK):
        return False
    return True


def check_write_file(test_file):
    if not os.access(test_file, os.W_OK):
        return False
    return True


def check_exists_file(test_file):
    if not os.access(test_file, os.F_OK):
        return False
    return True


def permissions(args):
    # check write permissions
    logger = logging.getLogger(__name__)

    if os.path.isdir(args.db_dir):
        if not check_write_dir(args.db_dir):
            raise RuntimeError('Failed write access to DB folder %s exiting....', args.db_dir)


    if os.path.isfile(args.db_file):
        if not check_write_file(args.db_file):
            raise RuntimeError('Failed write access to DB file %s exiting....', args.db_file)

    current_working_dir = os.getcwd()
    if not check_write_dir(current_working_dir):
        raise RuntimeError('Failed write access in current working folder %s exiting....', current_working_dir)

    if os.path.isdir(args.restore_dir):
        if not check_write_dir(args.restore_dir):
            raise RuntimeError('Restore DIR exists, but you do not have write access %s exiting....', args.restore_dir)
        else:
            logger.debug('Restore DIR exists %s', args.restore_dir)
    elif not os.path.isdir(args.restore_dir):
        if args.no_sim:
            try:
                os.makedirs(args.restore_dir)
            except:
                raise RuntimeError('Failed to create restore folder %s exiting....', args.restore_dir)
        else:
            logger.info('Simulating restore. Restore DIR does not exist, will need to create restore DIR %s', args.restore_dir)

    logger.info('Successfully passed all write access tests')


    # check stversion dir is readable
    if not os.access(args.versions_dir, os.R_OK):
        # print '''\nWalking directory "''' + args.versions_dir + '''" is not readable, exiting...'''
        logger.error('Read permissions of %s failed check exiting....', args.versions_dir)
        sys.exit(1)

    logger.info('Successfully passed stversion read access test')


def test_abs(test_dir):
    # check if dir is absolute
    if not os.path.isabs(test_dir):
        return False
    return True


def convert_to_abspath(rest_dir, comment='DIR'):
    # check if DIR is relative or absolute
    logger = logging.getLogger(__name__)
    logger.debug('%s is relative - Script DIR %s', comment, os.path.dirname(sys.argv[0]))
    logger.debug('%s is relative - Script called from %s', comment, os.getcwd())
    logger.debug('%s is relative - Converting to absolute using %s and %s', comment, os.getcwd(), rest_dir)
    if not os.path.isabs(rest_dir):
        abs_path = os.path.abspath(os.path.join(os.getcwd(), rest_dir))
        logger.debug('%s is relative - Converted to absolute %s', comment, abs_path)
    else:
        abs_path = rest_dir
        logger.debug('%s is absolute %s', comment, abs_path)
    return abs_path


def restoredir_check(abs_path, sync_dir):
    logger = logging.getLogger(__name__)
    logger.debug('Checking for %s in restore DIR path %s', sync_dir, abs_path)
    # regex looks for windows OS x:\ or linux OS /
    regex = re.compile(r'^(.:[\\]|[\/])$', re.I)
    while True:
        try:
            t_path = os.path.split(abs_path)
            abs_path = t_path[0]
            abs_versions_file = os.path.join(t_path[0], sync_dir)
            logger.debug('Checking in %s', abs_versions_file)
            if check_exists_file(abs_versions_file):
                logger.warning('Detected %s in restore path at %s', sync_dir, abs_path)
                return True
            elif re.search(regex, t_path[0]):
                # hit the root
                logger.debug('Did not detect %s in the restore path', sync_dir)
                return False
        except:
            return False


def warnuser():
    # found .stfolder or .stversions in path of where script is running from
    # need user to acknowledge they are running script potentially from sycthing dir
    # user input accepts enter and y to continue, anything else aborts
    logger = logging.getLogger(__name__)
    var = raw_input('''\nRestoring files to syncthing dir, recommend restoring to dir above syncthing dir,\nConfirm if you want to proceed... y/n [y]''')
    if var:
        if 'y' not in var:
            logger.debug('User acknowledged warning and chose to exit')
            sys.exit(1)
        logger.debug('User acknowledged warning and chose to continue')
        print '''Continuing...'''


def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return str("%02d:%02d:%02d" % (h, m, s))


def get_min_max_epoch(cli_epoch, plusminus):
  # calc min max epoch and return it
  plus_minus_seconds = (plusminus * 3600)
  epoch_max = cli_epoch + plus_minus_seconds
  epoch_min = cli_epoch - plus_minus_seconds
  return epoch_min, epoch_max


def get_before_epoch(cli_epoch, result_list):
  try:
    closest_numbers = filter(lambda x: x<=cli_epoch, result_list)
  except:
    closest_numbers = []
  return closest_numbers


def get_after_epoch(cli_epoch, result_list):
    try:
        closest_numbers = filter(lambda x: x>=cli_epoch, result_list)
    except:
        closest_numbers = []
    return closest_numbers


def get_epochs_btw_min_max(epoch_min, epoch_max, result_list):
    try:
        min_max_result_list = filter(lambda x: epoch_min <= x <= epoch_max, result_list)
    except:
        min_max_result_list = []
    return min_max_result_list


def check_file_exists(relative_file):
    # expects filename encoded the same as OS - UTF-8 encoded probably
    try:
        if os.path.isfile(relative_file):
            return True
        else:
            return False
    except:
        return False

