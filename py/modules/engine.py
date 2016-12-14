#import all constants
try:
    #this import will work when we are in scripts folder
    from config.config import *
except ImportError:
    print "Could not import config package. Try navigating to script folder before starting the script."
    exit()

import random
import string
import time
from datetime import datetime
import re

import out

#enable ftp buffering for all ftp calls. This list contains all the commands that have been tested yet and work.
enable_ftp_buffer = ['sync', 'sync_files', 'deploy', 'diff', 'backup_db', 'sync_db', 'upload_db']

finalizing_in_process = False

def get_random_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def get_random_secury_id():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))

#decorator for preparation and cleanup
def prepare_and_clean(func):
    import sys
    import out
    command = (sys._getframe(1).f_globals['__name__'])[3:]

    @out.indent
    def decorated_func(*args, **kwargs):
        start_time = time.time()
        initialize(command)
        result = func(*args, **kwargs)
        finalize()
        elapsed_time = "{:.3f}".format(time.time() - start_time)
        out.log('Done. Took ' + elapsed_time + ' seconds.')
        return result

    return decorated_func


#do not use out.indent on this, otherwise its output is indented and looks messy because there was no unindented output before
def initialize(command):
    import out
    import ftp
    out.clear_logfile()

    global enable_ftp_buffer
    if command in enable_ftp_buffer:
        out.log('enabling complete ftp buffering for ' + command + ' command', 'engine', out.LEVEL_DEBUG)
        ftp.start_buffer()

@out.indent
def finalize():
    import transfer
    import php
    import ftp
    import tmp
    out.log('finalizing', 'engine', out.LEVEL_INFO)

    #remember we are already finalizing, so we don't want to finalize again when something goes wrong during finalizing.
    global finalizing_in_process
    finalizing_in_process = True

    #always buffer finalization
    ftp.start_buffer()
    tmp.cleanup_remote()
    php.remove_command_file()
    tmp.remove_tmp_dir()
    #clean ftp buffer before cleaning up local, because we will create a local file in the process of ending the buffer
    ftp.end_buffer()
    tmp.cleanup_local()



def get_suffix(filename):
    #find the last slash
    slash_pos = filename.rfind('/')
    filename_without_path = filename[slash_pos+1:]
    #find the first dot in filename
    pos = filename_without_path.find('.')

    #this file has no suffix
    if pos == -1:
        return None
    else:
        #return suffix
        return filename_without_path[pos+1:]

def quit():
    if not finalizing_in_process:
        finalize()
        out.log('Exited with errors. Look at output/output.log for a detailed log.', 'engine', out.LEVEL_ERROR)
        exit()
    else:
        out.log('An error occured during finalizing. We ignore it and try to finish finalization.', 'engine', out.LEVEL_ERROR)

def clean_build_dir():
    import run
    run.local('rm -rf ' + LOCAL_BUILD_DIR)

#registers a new local filename and returns it. Does not actually create the file.
def get_new_local_file(suffix = None, create_file = False):
    import tmp

    if suffix is None:
        suffix = 'tmp'
    #get filename in tmp dir
    global local_tmp_files
    tmp_dir = tmp.get_local_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_').replace('.','_') + '.' + suffix

    #register file in current namespace
    tmp.register_local_file(filename)

    if create_file:
        import run
        run.local('touch ' + filename)
    
    #return filename
    return filename

#registers a new remote filename and returns it. Does not actually create the file.
def get_new_remote_file(suffix = None):
    import tmp
    if suffix is None:
        suffix = 'tmp'
    #get filenam ein tmp dir
    global remote_tmp_files
    tmp_dir = tmp.get_remote_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_').replace('.','_') + '.' + suffix

    #register file in current namespace
    tmp.register_remote_file(filename)

    #return file
    return filename


def get_database_dump_file(compression = False, domain = None):
    import run
    #mysql dump filenames
    if not os.path.isdir(LOCAL_DB_DIR):
        run.local('mkdir -p ' + LOCAL_DB_DIR)
    description = get_database_file_description(domain)
    filename = os.path.abspath(LOCAL_DB_DIR + '/' + description + '-' + str(datetime.now()).replace(' ', '-') + '.sql')
    if compression:
        filename += '.gz'
    return filename

def get_database_file_description(domain = None):
    if domain == 'local':
        description = 'dump-localhost'
    elif domain == 'remote':
        try:
            description = 'dump-' + LIVE_DOMAIN
        except NameError:
            description = 'dump-remote-unknown'
    elif domain is None:
        description = 'dump'
    else:
        out.log('Unknown domain: ' + str(domain), 'engine', out.LEVEL_ERROR)
        quit()

    return description

@out.indent
def get_latest_database_dump(domain = None):
    out.log('getting latest database dump file', 'engine', out.LEVEL_VERBOSE)
    #filter all files by description
    files = os.listdir(LOCAL_DB_DIR)
    timestamps = []
    description = get_database_file_description(domain)
    for f in files:
        if description in f:
            suffix = get_suffix(f)
            if suffix[-3:] == '.gz':
                timestamp = f[-33:]
                out.log('considering ' + f, 'engine', out.LEVEL_DEBUG)
            elif suffix[-4:] == '.sql':
                timestamp = f[-30:]
                out.log('considering '  + f, 'engine', out.LEVEL_DEBUG)
            else:
                out.log('unknown suffix, not considering ' + f, 'engine', out.LEVEL_DEBUG)
                continue

            timestamps.append(timestamp)
        else:
            out.log('not matching domain, not considering ' + f, 'engine', out.LEVEL_DEBUG)

    if len(timestamps) == 0:
        out.log('There is no database dump file with the description ' + description + ' and a correct suffix (allowed .gz and .sql).', 'engine', out.LEVEL_ERROR)
        quit()

    timestamps.sort()
    latest = timestamps[-1]
    for f in files:
        if description in f and latest in f:
            out.log('Latest database dump matching the domain is ' + f, 'engine', out.LEVEL_DEBUG)
            return os.path.join(LOCAL_DB_DIR, f)

    out.log('Something has gone wrong, this is probably a bug.', 'engine', out.LEVEL_ERROR)
    quit()

@out.indent
def get_remote_www_dir_abspath():
    import run
    out.log('getting absolute remote path of www directory', 'engine')
    filename = get_new_remote_file('out')
    run.remote('pwd >' + filename)
    return file.read_remote(filename).rstrip()

def sync_ftp():
    import ftp
    ftp.flush_buffer()

def split_by_encoding(item_list):
    ascii_list = []
    non_ascii_list = []
    for item in item_list:
        try:
            x = item.encode('ascii')
            ascii_list.append(item)
        except UnicodeEncodeError:
            non_ascii_list.append(item)
    return ascii_list, non_ascii_list

def escape(s):
    escape_table = {
        '"':'%22',
        '#':'%23',
        '$':'%24',
        '&':'%26',
        "'":'%27',
        '(':'%28',
        ')':'%29',
        '*':'%2A',
        '+':'%2B',
        ',':'%2C',
        '.':'%2E',
        '/':'%2F',
        ':':'%3A',
        ';':'%3B',
        '<':'%3C',
        '=':'%3D',
        '>':'%3E',
        '?':'%3F',
        '@':'%40',
        '[':'%5B',
        '\\':'%5C',
        ']':'%5D',
        '^':'%5E',
        '`':'%60',
        '{':'%7B',
        '|':'%7C',
        '}':'%7D',
        '~':'%7E'
    }
    #make sure to escape % first
    s = s.replace('%', '%25')

    #escape all other characters
    for character in escape_table:
        s = s.replace(character, escape_table[character])

    return s


def force_relative(path):
    if path[0] == '/':
        return path[1:]
    else:
        return path

def force_absolute(path):
    if path[0] != '/':
        return '/' + path
    else:
        return path

def path_join(*args):
    if(len(args)) == 0:
        return ''
    if(len(args)) == 1:
        return args[0]
    if len(args) > 2:
        return path_join(args[0], path_join(*args[1:]))

    #make sure we do not have neither trailing slash in a nor leading slash in b
    a = args[0]
    b = args[1]
    if a[-1] == '/':
        a = a[:-1]
    if b[0] == '/':
        b = b[1:]

    return a + '/' + b

