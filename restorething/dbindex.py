#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging

import rtdbtools
import rttools

    
def index_files_ondisk(cur, versdir):
    logger = logging.getLogger(__name__)
    last_root='_'
    last_file_nodate='_'
    
    if os.name == 'nt':
        # import module that fixes unicode problems
        import win_unicode_console
        win_unicode_console.enable()
        logger.debug('Detected windows based OS, fixing console UTF-8 support') 
        versdir = unicode(versdir)
    
    for root, subdirs, files in os.walk(versdir):
        subdirs.sort()
        files.sort()
        
        # get path without versioning dir in it
        orig_src_path = rtdbtools.remove_versioning_dir_from_path(root)
        logger.debug('Removed .stversions %s to %s', root, orig_src_path)
        
        for file in files:
            logger.debug('Processing %s %s', root, file)
            # strip date and time from filename
            file_nodate = rtdbtools.strip_file_date_time(file)
            # get date time from filename
            f_date, f_time = rtdbtools.get_file_date_time(root, file)
            
            # get epoch values
            try:
                f_epoch = rttools.get_epoch(f_date, f_time)
            except Exception, err:
                sys.stderr.write('ERROR: %s' % str(err))
                return 1
            
            # test for conflict string
            conflicted_flag=0
            if rtdbtools.check_file_conflict(file_nodate):
                conflicted_flag=1
                logger.debug('Detected syncthing conflict file')
            
            # confirm if original file exists
            deleted_flag=0
            
            # join original source path and file
            relative_file = os.path.join(orig_src_path, file_nodate)
            
            # if file will be considered deleted or renamed if return true
            if not rtdbtools.check_file_exists(relative_file):
                deleted_flag=1
            
            # if root dir is the same as last dir
            if root == last_root:
                id_root = last_id_root
                id_fo = last_id_fo
                id_fo_test = ''
                # current file_out is not the same as last file_out, test if already exists file_out to DB
                if file_nodate != last_file_nodate:
                    # before testing using sql filter use list of lists to confirm if exists, this is an attempt to optimise
                    for row in outfile_lol:
                        if row[2] in file_nodate:
                            id_fo_test = row[0]
                            break
                    if not id_fo_test:
                        id_fo = rtdbtools.insert_table_file_out(cur, id_root, file_nodate, conflicted_flag, deleted_flag)
                        # add current outfile to list of lists due to not existing yet
                        outfile_lol.append([id_fo, id_root, file_nodate])
                    else:
                        id_fo = id_fo_test
                # insert file_in into DB
                rtdbtools.insert_table_file_in(cur, id_fo, file, f_date, f_time, f_epoch)
                
            else:
                logger.debug('Indexing new sub directory')
                # clear outfile list of lists due to change of dir
                outfile_lol=[]
                # check if root dir exists in db, even thou not the same as last file tested above
                try:
                    cur.execute('''SELECT id_dir FROM tb_dir_in WHERE dir=?''', (root,))
                    id_root = cur.fetchone()[0]
                except:
                    id_root = rtdbtools.insert_table_dir_in(cur, root)
                    id_fo = rtdbtools.insert_table_file_out(cur, id_root, file_nodate, conflicted_flag, deleted_flag) 
                    rtdbtools.insert_table_file_in(cur, id_fo, file, f_date, f_time, f_epoch)
                    #  update last variables for next loop
                    last_id_root, last_id_fo, last_root, last_file_nodate = rtdbtools.update_last_variables(id_root, id_fo, root, file_nodate)
                    # add current outfile to list of lists, due to not existing yet
                    outfile_lol.append([id_fo, id_root, file_nodate])
                    # goto next file in loop
                    continue     
                # get row_id if fields match DIR ID and filename from file_out table
                # if no match add DIR to dir_in table, then grab last ID
                try: 
                    cur.execute('''SELECT * FROM tb_file_out WHERE id_dir=? AND filename_out=?''', (id_root, file_nodate))
                    id_fo = cur.fetchone()[0] 
                except:
                    id_fo = rtdbtools.insert_table_file_out(cur, id_root, file_nodate, conflicted_flag, deleted_flag)
                    # add current outfile to list of lists, due to not existing yet
                    outfile_lol.append([id_fo, id_root, file_nodate])
                # add file to DB
                rtdbtools.insert_table_file_in(cur, id_fo, file, f_date, f_time, f_epoch)  
            # update last variables for next loop
            last_id_root, last_id_fo, last_root, last_file_nodate = rtdbtools.update_last_variables(id_root, id_fo, root, file_nodate)


def main(dbfile, nofrz, versdir):
    '''
    Index DB file
    '''
    logger = logging.getLogger(__name__)
    # freeze time 24hrs 86400, 1hr 3600
    frz_time = 86400 
    if nofrz:
        db_mod_time = True
    else:
        db_mod_time = rtdbtools.process_db_mod_time(frz_time, dbfile)
      
    if db_mod_time:
        logger.info('Generating a fresh DB file')
        ## init db and cursor - create tables
        tic = int(time.clock())
        con = rtdbtools.init_db(dbfile)
        with con:
            cur = con.cursor()
            rtdbtools.create_db(cur)
            index_files_ondisk(cur, versdir)   
            
        toc = int(time.clock())
        formated_time = rttools.format_time(toc - tic)
        
        logger.info('Finished indexing filesystem, total time ' + formated_time + ', proceeding with recovery')  
        logger.debug('DB index start ' + str(tic) + ' end ' + str(toc) + ' total ' + formated_time)
    else:
        logger.info('DB file last modification is less than 24 hours, using existing DB file')    
