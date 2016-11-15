import engine
import out
import os
import fnmatch
import run
import json
import transfer
import re
import unicodedata
from codecs import open


NORMALIZE_UNICODE_FILENAMES = True
NORMALIZATION_FORM = 'NFKC'

#upload local files using ftp
@out.indent
def upload(force_upload = False, destructive = False, server_owned = None):
    out.log('comparing md5 hashes of local and remote files', 'sync')

    respect_server_owned = (server_owned != 'server-owned')

    #recalculate all md5 hashes
    files_local = create_md5_table()

    if engine.ALWAYS_RECALCULATE_MD5_TABLE:
        #calculate remote files
        files_remote = create_remote_md5_table()
    else:
        #or just remember the files we uploaded last time
        files_remote = load_md5_table(engine.LOCAL_MD5_TABLE_FILE)

    #check which have changed
    files_scheduled = []
    for f in files_local:
        if force_upload or (not f in files_remote) or (not files_local[f] == files_remote[f]):
            if ignored_file(f) or system_file(f):
                out.log('ignoring ' + f, 'sync', out.LEVEL_DEBUG)
            else:
                if respect_server_owned and (f in files_remote) and server_owned_file(f):
                    out.log('ignoring server owned file ' + f, 'sync', out.LEVEL_INFO)
                else:
                    out.log('scheduled for upload: ' + f, 'sync', out.LEVEL_INFO)
                    files_scheduled.append(f)

    #upload new or modified files
    if len(files_scheduled) > 0:
        out.log('uploading ' + str(len(files_scheduled)) + ' files.', 'sync')
        transfer.put_multiple(files_scheduled)
    else:
        out.log('all files are up to date, not uploading any files.', 'sync')

    #delete all other files
    if destructive:
        files_scheduled_for_removal = []
        for f in files_remote:
            if not f in files_local:
                if system_file(f):
                    out.log('skipping removal of system file ' + f, 'sync', out.LEVEL_VERBOSE)
                elif ignored_file(f):
                    out.log('skipping removal of ignored file ' + f, 'sync', out.LEVEL_VERBOSE)
                else:
                    out.log('scheduled for removal: ' + f, 'sync', out.LEVEL_INFO)
                    files_scheduled_for_removal.append(f)

        #delete superfluous files
        if len(files_scheduled_for_removal) > 0:
            out.log('removing ' + str(len(files_scheduled_for_removal)) + ' files.', 'sync')
            transfer.remove_remote_multiple(files_scheduled_for_removal)
        else:
            out.log('no unwanted files found, not removing any files.', 'sync')


    #save current local list to file, butu only if it is being actually used
    if not engine.ALWAYS_RECALCULATE_MD5_TABLE:
        save_md5_table(files_local)

def download(force_download = False, destructive = False):
    out.log('ignoring files matching these regex patterns: ' + str(engine.IGNORE_ON_SYNC_REGEX_LIST), 'sync', out.LEVEL_DEBUG)
    out.log('comparing md5 hashes of local and remote files', 'sync')

    if not force_download or destructive:
        #recalculate all md5 hashes
        files_local = create_md5_table()
        #calculate remote files
        files_remote = create_remote_md5_table()

        #check which have changed
        files_scheduled = []
        for f in files_remote:
            if not (ignored_file(f) or system_file(f)) and (force_download or not f in files_local or not files_local[f] == files_remote[f]):
                out.log('scheduled for download: ' + f, 'sync', out.LEVEL_INFO)
                files_scheduled.append(f)

        #download new or modified files
        if len(files_scheduled) > 0:
            out.log('downloading ' + str(len(files_scheduled)) + ' files.', 'sync')
            transfer.get_multiple(files_scheduled)
        else:
            out.log('all files are up to date, not downloading any files.', 'sync')
    else:
        out.log('downloading all files', 'sync')
        transfer.get_directory('.')

    #delete all other files
    if destructive:
        files_scheduled_for_removal = []
        for f in files_local:
            if not f in files_remote:
                if system_file(f):
                    out.log('skipping removal of system file ' + f, 'sync', out.LEVEL_VERBOSE)
                elif ignored_file(f):
                    out.log('skipping removal of ignored file ' + f, 'sync', out.LEVEL_VERBOSE)
                else:
                    out.log('scheduled for removal: ' + f, 'sync', out.LEVEL_INFO)
                    files_scheduled_for_removal.append(os.path.abspath(engine.LOCAL_WWW_DIR + '/' + f))

        #delete superfluous files
        if len(files_scheduled_for_removal) > 0:
            out.log('removing ' + str(len(files_scheduled_for_removal)) + ' files.', 'sync')
            transfer.remove_local_multiple(files_scheduled_for_removal)
        else:
            out.log('no unwanted files found, not removing any files.', 'sync')


    #save current remote list to file, but don't bother if it is not being used anyway
    if not engine.ALWAYS_RECALCULATE_MD5_TABLE:
        save_md5_table(files_remote)


#print a diff between the server and the 
@out.indent
def diff():
    out.log('comparing remote files with local files', 'sync')

    #create md5 tables
    files_local = create_md5_table()
    files_remote = create_remote_md5_table()

    local_new = 0
    remote_new = 0
    modified = 0

    #local files not on server
    for f in files_local:
        if not f in files_remote:
            if system_file(f):
                out.log('skipping new local system file: ' + f,'sync', out.LEVEL_VERBOSE)
            elif ignored_file(f):
                out.log('skipping new local ignored file: ' + f, 'sync', out.LEVEL_VERBOSE)
            else:
                out.log('new local file: ' + f, 'sync')
                local_new += 1
    #remote files not on local
    for f in files_remote:
        if not f in files_local:
            if system_file(f):
                out.log('skipping new remote system file: ' + f,'sync', out.LEVEL_VERBOSE)
            elif ignored_file(f):
                out.log('skipping new remote ignored file: ' + f, 'sync', out.LEVEL_VERBOSE)
            else:
                out.log('new remote file: ' + f, 'sync')
                remote_new += 1
    #modified files
    for f in files_local:
        if f in files_remote and files_local[f] != files_remote[f]:
            if system_file(f):
                out.log('skipping modified system file: ' + f,'sync', out.LEVEL_VERBOSE)
            elif ignored_file(f):
                out.log('skipping modified ignored file: ' + f, 'sync', out.LEVEL_VERBOSE)
            else:
                out.log('modified file: ' + f, 'sync')
                modified += 1


    out.log('Summary:', 'sync')
    if local_new == 0 and remote_new == 0 and modified == 0:
        out.log('All files are in sync.', 'sync')
    else:
        out.log('New local files: ' + str(local_new), 'sync')
        out.log('New remote files: ' + str(remote_new), 'sync')
        out.log('Modified files: ' + str(modified), 'sync')

    file = open('tmp/local.md5', 'w')
    json.dump(files_local, file)
    file.close()
    file = open('tmp/remote.md5', 'w')
    json.dump(files_remote, file)
    file.close()


def match_file(file, regex_list):
    for regex in regex_list:
        if re.search(regex, file) is not None:
            return True
    return False

def ignored_file(file):
    return match_file(file, engine.IGNORE_ON_SYNC_REGEX_LIST)

def system_file(file):
    return match_file(file, engine.DEPLOY_TOOLS_SYSTEM_FILES_REGEX_LIST)

def server_owned_file(file):
    return match_file(file, engine.SERVER_OWNED_REGEX_LIST)

def save_md5_table(md5_table):
    md5_table_file = open(engine.LOCAL_MD5_TABLE_FILE, 'w', encoding='utf-8')
    json.dump(md5_table, md5_table_file)
    md5_table_file.close()

@out.indent
def load_md5_table(filename):
    out.log('loading hash table from ' + filename, 'sync')
    engine.sync_ftp()
    try:
        #load form file
        md5_table_file = open(filename, 'r', encoding='utf-8')
        md5_table = json.load(md5_table_file)
        md5_table_file.close()
    except:
        #if that fails: return empty table
        out.log('unable to load hashtable from ' + filename + ', creating empty table.', 'sync', out.LEVEL_WARNING)
        md5_table = {}

    #normalize unicode entries
    if NORMALIZE_UNICODE_FILENAMES:
        normalized_md5_table = {}
        for key in md5_table:
            if isinstance(key, str):
                key = unicode(key, 'utf-8')
            normalized_key = unicodedata.normalize(NORMALIZATION_FORM, key)
            normalized_md5_table[normalized_key] = md5_table[key]
        md5_table = normalized_md5_table

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
            if isinstance(rel_file, str):
                rel_file = unicode(rel_file, 'utf-8')
            if NORMALIZE_UNICODE_FILENAMES:
                rel_file = unicodedata.normalize(NORMALIZATION_FORM, rel_file)
            files.append(rel_file)

    for f in files:
        if not (ignored_file(f) or system_file(f)):
            try:
                md5_table[f] = engine.md5sum(f)
            except IndexError:
                pass
            except IOError:
                out.log('could not open ' + f, 'sync', out.LEVEL_WARNING)

    return md5_table
