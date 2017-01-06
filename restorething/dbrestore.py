#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import logging
import shutil

import rtdbtools
import rttools

def db_getrowout(cur, args):
    logger = logging.getLogger(__name__)

    # set restore conflict and deleted/renamed files flags
    if args.inc_conflict:
        inc_conf_filter = 1
    else:
        inc_conf_filter = 0

    if args.no_delete:
        no_del_filter = 0
    else:
        no_del_filter = 1

    if args.filter_file is not None:
        logger.debug('Filtering based on file %s', args.filter_file)

        # query tables file_out and dir_in and filter by args.no_delete and args.inc_conflict string matching filename
        cur.execute('''SELECT di.*, fo.* \
                    FROM tb_file_out fo \
                    INNER JOIN tb_dir_in di \
                    ON fo.id_dir = di.id_dir \
                    WHERE fo.conflict_flag <= (?) AND fo.delete_flag <= (?) AND fo.filename_out LIKE (?)''', (inc_conf_filter, no_del_filter,'%'+args.filter_file+'%'))

    elif args.filter_dir is not None:
        logger.debug('Filtering based on DIR %s', args.filter_dir)

        # query tables file_out and dir_in and filter by args.no_delete and args.inc_conflict and string matching dir
        cur.execute('''SELECT di.*, fo.* \
                    FROM tb_file_out fo \
                    INNER JOIN tb_dir_in di \
                    ON fo.id_dir = di.id_dir \
                    WHERE fo.conflict_flag <= (?) AND fo.delete_flag <= (?) AND di.dir LIKE (?)''', (inc_conf_filter, no_del_filter,'%'+args.filter_dir+'%'))

    elif args.filter_allinstances is not None:
        logger.debug('Restoring all instances of %s', args.filter_allinstances)

        f_dir, f_file = os.path.split(args.filter_allinstances)
        logger.debug('Restoring all instances of DIR = %s, File = %s', f_dir, f_file)
        # query tables file_out and dir_in and filter by args.no_delete and args.inc_conflict and string matching dir
        cur.execute('''SELECT di.*, fo.* \
                    FROM tb_file_out fo \
                    INNER JOIN tb_dir_in di \
                    ON fo.id_dir = di.id_dir \
                    WHERE fo.conflict_flag <= (?) AND fo.delete_flag <= (?) AND di.dir_orig LIKE (?) AND fo.filename_out LIKE (?)''', (inc_conf_filter, no_del_filter, f_dir, f_file))

    else:
        logger.debug('No file or DIR filtering')
        # query tables file_out and dir_in and filter by args.no_delete and args.inc_conflict
        cur.execute('''SELECT di.*, fo.* \
                    FROM tb_file_out fo \
                    INNER JOIN tb_dir_in di \
                    ON fo.id_dir = di.id_dir \
                    WHERE fo.conflict_flag <= (?) AND fo.delete_flag <= (?)''', (inc_conf_filter, no_del_filter))

    # grab all from above sql statement
    row_out = cur.fetchall()
    return cur, row_out


def db_getrowin(cur, x, args):
    # get all versions of a file using file out ID
    cur.execute('''SELECT fi.* \
                FROM tb_file_in fi \
                INNER JOIN tb_file_out fo \
                ON fo.id_file_out = fi.id_file_out \
                WHERE fi.id_file_out=(?) \
                ORDER BY fi.epoch''', (x[3],))

    # fetch all into a list of lists
    row_in = cur.fetchall()
    return cur, row_in


def get_required_epoch(x, row_in, cli_epoch, args):
    logger = logging.getLogger(__name__)

    # iterate list of lists and pull out only epochs into list
    result_list = [ y[5] for y in row_in ]
    logger.debug('Processing file ---- %s', x[5])
    logger.debug('Processing file ---- epochs to choose from %s', result_list)

    # check both sides based on hour, first looking on early side
    if args.plus_minus > 0:
        epoch_min, epoch_max = rttools.get_min_max_epoch(cli_epoch, args.plus_minus)
        logger.debug('Restoring +/- timestamps epoch %s min %s max %s', str(cli_epoch), str(epoch_min), str(epoch_max))
        min_max_result_list = rttools.get_epochs_btw_min_max(epoch_min, epoch_max, result_list)
        logger.debug('Restoring +/- list of suitable epochs %s', min_max_result_list)
        if min_max_result_list:
            closest_numbers = rttools.get_before_epoch(cli_epoch, min_max_result_list)
            logger.debug('Restoring +/- list of suitable epochs before %s', closest_numbers)
            if closest_numbers:
                closest = max(closest_numbers)
                logger.debug('Restoring +/- found epoch before %s', closest)
            else:
                closest_numbers = rttools.get_after_epoch(cli_epoch, min_max_result_list)
                logger.debug('Restoring +/- list of epochs after %s', closest_numbers)
                if closest_numbers:
                    closest = min(closest_numbers)
                    logger.debug('Restoring +/- found epoch after %s', closest)
                else:
                    logger.debug('Restoring +/- timestamp %s - No file found between %s and %s, skipping file', str(cli_epoch), str(epoch_min), str(epoch_max))
                    return True, True
        else:
            logger.debug('Restoring +/- timestamp %s - No file found between %s and %s, skipping file', str(cli_epoch), str(epoch_min), str(epoch_max))
            return True, True
    # looks on early side
    elif args.before > 0:
        closest_numbers = rttools.get_before_epoch(cli_epoch, result_list)
        logger.debug('Restoring before %s list of suitable epochs before %s', cli_epoch, closest_numbers)
        if closest_numbers:
            closest = max(closest_numbers)
            logger.debug('Restoring before found epoch before %s', closest)
        else:
            logger.debug('Restoring before timestamp %s - No file found, skipping file', str(cli_epoch))
            return True, True
    # looks on later side
    elif args.after > 0:
        closest_numbers = rttools.get_after_epoch(cli_epoch, result_list)
        logger.debug('Restoring after %s list of suitable epochs after %s', cli_epoch, closest_numbers)
        if closest_numbers:
            closest = min(closest_numbers)
            logger.debug('Restoring after found epoch after %s', closest)
        else:
            logger.debug('Restoring after timestamp %s - No file found, skipping file', str(cli_epoch))
            return True, True
    # default behaviour look on early side of epoch and then later side
    else:
        closest_numbers = rttools.get_before_epoch(cli_epoch, result_list)
        logger.debug('Restoring before %s list of suitable epochs before %s', cli_epoch, closest_numbers)
        if closest_numbers:
            closest = max(closest_numbers)
            logger.debug('Restoring before found epoch before %s', closest)
        else:
            closest_numbers = rttools.get_after_epoch(cli_epoch, result_list)
            logger.debug('Restoring after %s list of suitable epochs after %s', cli_epoch, closest_numbers)
            closest = min(closest_numbers)
            logger.debug('Restoring after found epoch after %s', closest)

    return closest, False


def restore_file(final_results, restdir_abs_path, args):
    # preps dest dir, src and dst filenames, then restore file

    dst_dir = process_dir(final_results, restdir_abs_path, args.no_sim)
    ue_src_file, ue_dst_file = encode_filenames(final_results, dst_dir, args)
    if dst_dir:
        copy_files(ue_src_file, ue_dst_file, args.no_sim)
    else:
        logger.error('Failed to create destination DIR skipping file %s', ue_dst_file)


def process_dir(final_results, rest_dir, no_sim):
    # going to need restore directory
    logger = logging.getLogger(__name__)

    #prep dest DIR
    if os.path.isabs(final_results[1]):
        split_path = os.path.splitdrive(final_results[1])
        cleaned_dir = split_path[1]
        logger.debug('Path is absolute removing drive from path %s', split_path[1])
    else:
        cleaned_dir = final_results[1]
        logger.debug('Path is not absolute %s', final_results[1])

    regex = re.compile(r'^([\\\/]|\.\.[\\\/])', re.I)
    cleaned_path = regex.sub(r'', cleaned_dir)
    logger.debug('Removing proceeding dots and slashes %s', cleaned_path)

    dst_dir = os.path.join(rest_dir, cleaned_path)
    logger.debug('Final restore path %s', dst_dir)

    if not os.path.exists(dst_dir):
        if no_sim:
            try:
                os.makedirs(dst_dir)
                logger.info('Creating destination DIR %s', dst_dir)
            except:
                return False
        else:
          logger.debug('Simulate creating destination DIR %s', dst_dir)
    else:
        logger.debug('Destination DIR exists %s', dst_dir)
    return dst_dir


def encode_filenames(final_results, dst_dir, args):
    # going to need restore directory
    logger = logging.getLogger(__name__)

    # prep src dst file
    src_file = os.path.join(final_results[0], final_results[2])
    if args.filter_allinstances is not None:
        dst_file = os.path.join(dst_dir, final_results[2])
    else:
        dst_file = os.path.join(dst_dir, final_results[3])

    # no need to play with encoding decoding stuff due to importing win_unicode_console earlier
    # when detecting windows based OS
    if os.name == 'nt':
        return src_file, dst_file
    else:
        ue_src_file = src_file.encode('utf-8')
        ue_dst_file = dst_file.encode('utf-8')
    return ue_src_file, ue_dst_file


def copy_files(ue_src_file, ue_dst_file, no_sim):
    # going to need restore directory
    logger = logging.getLogger(__name__)

    # if source exists
    if rttools.check_file_exists(ue_src_file):
        if rttools.check_file_exists(ue_dst_file):
            logger.warning('Destination file exists overwriting %s', ue_dst_file)
        if no_sim:
            try:
                shutil.copy(ue_src_file, ue_dst_file)
                logger.debug('Successfully restored from %s', ue_src_file)
                logger.info('Successfully restored too %s', ue_dst_file)
            except Exception as err:
                logger.error('Failed to restore file from %s', ue_src_file)
                logger.error('Failed to restore file too %s', ue_dst_file)
                logger.error('Failed with error %s', err)
        else:
          logger.debug('Simulate restoring from %s', ue_src_file)
          logger.info('Simulate restoring too %s', ue_dst_file)
    else:
      logger.error('Restore failed, source does not exist, src = %s', ue_src_file)
      logger.debug('Restore failed, source does not exist, dst = %s', ue_dst_file)


def main(cli_epoch, restdir_abs_path, args):
    '''
    Restore files from DB file
    '''
    logger = logging.getLogger(__name__)
    logger.info('Starting restore process')
    con = rtdbtools.init_db(args.db_file)
    with con:
        cur = con.cursor()
        cur, row_out = db_getrowout(cur, args)

        row_count = len(row_out)
        logger.debug('Archive query returned %s results - row_out', row_count)
        if row_count < 1:
            logger.info('Archive query returned %s results, nothing to restore, exiting...', row_count)
            sys.exit(1)

        for x in row_out:
            cur, row_in = db_getrowin(cur, x, args)

            if args.filter_allinstances is not None:
                row_count = len(row_in)
                logger.debug('Archive query returned %s results - row_in', row_count)
            else:
                closest, flag_continue = get_required_epoch(x, row_in, cli_epoch, args)
                if flag_continue:
                    logger.debug('Restoring +/- continuing .....')
                    continue

            for z in row_in:
                if args.filter_allinstances is not None:
                    final_results = [x[1], x[2], z[2], x[5], z[5]]
                    restore_file(final_results, restdir_abs_path, args)
                else:
                    if closest in (z):
                        final_results = [x[1], x[2], z[2], x[5], z[5]]
                        restore_file(final_results, restdir_abs_path, args)
                        break