import engine
import out
import os
import fnmatch
import run
import json
import hashlib
import transfer
import re

#upload local files using ftp
@out.indent
def upload(force_upload = False, recalculate_remote = True):
    out.log('comparing md5 hashes of local and remote files', 'sync')

    #recalculate all md5 hashes
    files_local = create_md5_table()

    if recalculate_remote:
        #calculate remote files
        files_remote = create_remote_md5_table()
    else:
        #or just remember the files we uploaded last time
        files_remote = load_md5_table(engine.LOCAL_MD5_TABLE_FILE)

    #check which have changed
    files_scheduled = []
    for f in files_local:
        if not ignored_file(f) and (force_upload or not f in files_remote or not files_local[f] == files_remote[f]):
            out.log('scheduled for upload: ' + f, 'sync', out.LEVEL_INFO)
            files_scheduled.append(f)

    #upload new or modified files
    if len(files_scheduled) > 0:
        out.log('uploading ' + str(len(files_scheduled)) + ' files.', 'sync')
        transfer.put_multiple(files_scheduled)
    else:
        out.log('nothing to do, all files up to date.', 'sync')

    #save current local list to file
    save_md5_table(files_local)

def download(force_download = False):
    out.log('ignoring files matching these regex patterns: ' + str(engine.IGNORE_ON_SYNC_REGEX_LIST), 'sync', out.LEVEL_DEBUG)
    out.log('comparing md5 hashes of local and remote files', 'sync')

    #recalculate all md5 hashes
    files_local = create_md5_table()
    #calculate remote files
    files_remote = create_remote_md5_table()

    #check which have changed
    files_scheduled = []
    for f in files_remote:
        if not ignored_file(f) and (force_download or not f in files_local or not files_local[f] == files_remote[f]):
            out.log('scheduled for download: ' + f, 'sync', out.LEVEL_INFO)
            files_scheduled.append(f)

    #upload new or modified files
    if len(files_scheduled) > 0:
        out.log('downloading ' + str(len(files_scheduled)) + ' files.', 'sync')
        transfer.get_multiple(files_scheduled)
    else:
        out.log('nothing to do, all files up to date.', 'sync')

    #save current remote list to file
    save_md5_table(files_remote)

@out.indent
def ignored_file(file):
    for regex in engine.IGNORE_ON_SYNC_REGEX_LIST:
        if re.search(regex, file) is not None:
            out.log('ignoring ' + file, 'sync', out.LEVEL_DEBUG)
            return True
    return False


def md5sum(filename):
    md5 = hashlib.md5()
    with open(os.path.join(engine.LOCAL_WWW_DIR, filename), 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def save_md5_table(md5_table):
    md5_table_file = open(engine.LOCAL_MD5_TABLE_FILE, 'w')
    json.dump(md5_table, md5_table_file)
    md5_table_file.close()

@out.indent
def load_md5_table(filename):
    out.log('loading hash table from ' + filename, 'sync')
    try:
        #load form file
        md5_table_file = open(filename, 'r')
        md5_table = json.load(md5_table_file)
        md5_table_file.close()
    except:
        #if that fails: return empty table
        md5_table = {}

    #give back
    return md5_table

@out.indent
def create_remote_md5_table():
    #register new remote file
    remote_md5_table_file = engine.get_new_remote_file('json')
    #run script to create md5 hashes on the remote
    out.log('calculating remote md5 hashes', 'sync')
    run.remote_python_script(engine.SCRIPT_DIR + '/py/scripts/create_md5_table.py', engine.NORM_WWW_DIR + ' ' + remote_md5_table_file)
    #download table file
    out.log('download remote hash table', 'sync', out.LEVEL_VERBOSE)
    md5_table_file = transfer.get(remote_md5_table_file)
    #load it
    md5_table = load_md5_table(md5_table_file)
    #and return it
    return md5_table


@out.indent
def create_md5_table():
    out.log('calculating local md5 hashes', 'sync')
    files = []
    md5_table = {}
    for root, dirnames, filenames in os.walk(engine.LOCAL_WWW_DIR):
        #for filename in fnmatch.filter(filenames, '*'):
        for filename in filenames:
            abs_file = os.path.join(root, filename)
            rel_file = abs_file[len(engine.LOCAL_WWW_DIR)+1:]
            files.append(rel_file)

    for f in files:
        try:
            md5_table[f] = md5sum(f)
        except IndexError:
            pass

    return md5_table
