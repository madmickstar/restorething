#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import rttools
import ConfigParser
from ConfigParser import RawConfigParser


def validate_ini(logging_file):
    ''' Validate the retrieved INI file, review sections and some fields '''
    parser = ConfigParser.RawConfigParser(allow_no_value=True)
    try:
        parser.read(logging_file)
    except Exception as e:
        raise RuntimeError('The retrieved ini has an error. Reason: %s' % e)

    h = re.split('[ ,]{1,2}',parser.get('handlers', 'keys'))
    f = re.split('[ ,]{1,2}',parser.get('formatters', 'keys'))
    
    h_class = ('FileHandler','StreamHandler')
    h_level = ('info','warning','error','debug','critical')
    for key in (h):
        hk = 'handler_'+key
        if hk in parser.sections():
            hk_class = parser.get(hk, 'class')
            hk_level = parser.get(hk, 'level')
            hk_format = parser.get(hk, 'formatter')
            if hk_class not in h_class:
                raise RuntimeError('ini has an error. Reason: %s bad value class = %s' % (hk, hk_class))
            if hk_level.lower() not in h_level:
                raise RuntimeError('ini has an error. Reason: %s bad value level = %s' % (hk, hk_level))
            if hk_format not in f:
                raise RuntimeError('ini has an error. Reason: %s bad value formatter = %s' % (hk, hk_format))
        else:
            raise RuntimeError('ini has an error. Reason: %s section does not exist' % hk)
 
    for key in (f):
        fk = 'formatter_'+key
        if fk not in parser.sections():
            raise RuntimeError('ini has an error. Reason: %s section does not exist' % fk)


def create_ini(logging_file, console_level="INFO"):
    print "::\n:: Adding logging config  to " + logging_file + "\n::"
    config = ConfigParser.RawConfigParser()
    '''
    loggers settings
    '''
    config.add_section('loggers')
    config.set('loggers', 'keys', "root")
    '''
    handlers settings
    '''
    config.add_section('handlers')
    config.set('handlers', 'keys', "console,info_file,error_file,debug_file")
    '''
    formatters settings
    '''
    config.add_section('formatters')
    config.set('formatters', 'keys', "simple,brief,precise")
    '''
    logger_root settings
    '''
    config.add_section('logger_root')
    config.set('logger_root', 'level', "NOTSET")
    config.set('logger_root', 'handlers', "console,info_file,error_file,debug_file")
    '''
    handler_* settings
    '''
    config.add_section('handler_console')
    config.set('handler_console', 'class', "StreamHandler")
    config.set('handler_console', 'level', console_level)
    config.set('handler_console', 'formatter', "brief")
    config.set('handler_console', 'args', "(sys.stdout,)")
    config.add_section('handler_info_file')
    config.set('handler_info_file', 'class', "FileHandler")
    config.set('handler_info_file', 'level', "INFO")
    config.set('handler_info_file', 'formatter', "simple")
    config.set('handler_info_file', 'encoding', "utf8")
    config.set('handler_info_file', 'args', "('info.log', 'w')")
    config.add_section('handler_error_file')
    config.set('handler_error_file', 'class', "FileHandler")
    config.set('handler_error_file', 'level', "ERROR")
    config.set('handler_error_file', 'formatter', "simple")
    config.set('handler_error_file', 'encoding', "utf8")
    config.set('handler_error_file', 'args', "('error.log', 'w')")
    config.add_section('handler_debug_file')
    config.set('handler_debug_file', 'class', "FileHandler")
    config.set('handler_debug_file', 'level', "DEBUG")
    config.set('handler_debug_file', 'formatter', "precise")
    config.set('handler_debug_file', 'encoding', "utf8")
    config.set('handler_debug_file', 'args', "('debug.log', 'w')")
    '''
    formatter_* settings
    '''
    config.add_section('formatter_simple')
    config.set('formatter_simple', 'format', "%(asctime)s - %(levelname)-8s - %(name)-10s - %(message)s")
    config.set('formatter_simple', 'datefmt', "%Y-%m-%d %H:%M:%S")
    config.set('formatter_simple', 'class', "logging.Formatter")
    config.add_section('formatter_brief')
    config.set('formatter_brief', 'format', "%(levelname)-8s : %(name)-10s : %(message)s")
    config.set('formatter_brief', 'datefmt', "")
    config.set('formatter_brief', 'class', "logging.Formatter")
    config.add_section('formatter_precise')
    config.set('formatter_precise', 'format', "%(asctime)s - %(levelname)-8s - %(name)-10s - %(message)s")
    config.set('formatter_precise', 'datefmt', "")
    config.set('formatter_precise', 'class', "logging.Formatter")

    try:
        with open(logging_file, 'w') as f:
    	    config.write(f)
    except IOError, err:
        raise RuntimeError('ERROR: Failed to create logging config file, Reason: %s' % err)


def main(args):
    current_working_dir = os.getcwd()
    if not rttools.check_write_dir(current_working_dir):
        sys.stderr.write('ERROR: Failed write access in current working folder %s exiting....' % current_working_dir)
        sys.exit(1)

    if args.debug:
        logging_file='logging_debug.ini'
        create_ini(logging_file, "DEBUG")
    else:
        logging_file='logging.ini'
        if logging_file not in os.listdir('.'):
            try:
                create_ini(logging_file)
            except Exception, err:
                sys.stderr.write('ERROR: %s' % str(err))
                sys.exit(1)
        else:
            try:
                validate_ini(logging_file)
            except Exception, err:
                sys.stderr.write('ERROR: %s' % str(err))
                sys.exit(1)
    return logging_file


if __name__ == "__main__":
    main()