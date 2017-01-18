#import all constants
try:
    #this import will work when we are in scripts folder
    from config.config import *
except ImportError:
    print "Could not import config package. Try navigating to script folder before starting the script."
    exit()

import random
import string
import hashlib
import time
from datetime import datetime
import re
from codecs import open

import out

#enable ftp buffering for all ftp calls. This list contains all the commands that have been tested yet and work.
enable_ftp_buffer = ['sync', 'sync_files', 'deploy', 'diff', 'backup_db', 'sync_db', 'upload_db']

current_tmp_file_namespace = 'global'
finalizing_in_process = False

#remember the files we have created for cleaning up later
local_tmp_files = {}
local_tmp_files['global'] = []
remote_tmp_files = {}
remote_tmp_files['global'] = []

start_time = time.time()

remote_tmp_dir_created = False

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
        global start_time
        start_time = time.time()
        initialize(command)
        result = func(*args, **kwargs)
        finalize()
        elapsed_time = "{:.3f}".format(time.time() - start_time)
        out.log('Done. Took ' + elapsed_time + ' seconds.')
        return result

    return decorated_func

#decorator for cleaning up immediately
def cleanup_tmp_files(func):
    def cleanup_immediately_func(*args, **kwargs):
        #change but remember namespace
        global current_tmp_file_namespace
        old_tmp_file_namespace = current_tmp_file_namespace
        current_tmp_file_namespace = get_random_id()
        local_tmp_files[current_tmp_file_namespace] = []
        remote_tmp_files[current_tmp_file_namespace] = []
        result = func(*args, **kwargs)
        cleanup(current_tmp_file_namespace)
        current_tmp_file_namespace = old_tmp_file_namespace
        return result
    return cleanup_immediately_func

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
    global remote_tmp_dir_created
    import transfer
    import php
    import ftp
    out.log('finalizing', 'engine', out.LEVEL_INFO)

    #remember we are already finalizing, so we don't want to finalize again when something goes wrong during finalizing.
    global finalizing_in_process
    finalizing_in_process = True

    #always buffer finalization
    ftp.start_buffer()
    cleanup_remote()
    php.remove_command_file()
    if remote_tmp_dir_created:
        transfer.remove_remote_directory(NORM_TMP_DIR)
        remote_tmp_dir_created = False
    #clean ftp buffer before cleaning up local, because we will create a local file in the process of ending the buffer
    ftp.end_buffer()

    cleanup_local()


#cleanup is being run at the very end. cleans up all the files that have been created in the process.
@out.indent
def cleanup(namespace = None, local = True, remote = True):
    #cleanup all namespaces
    if namespace is None:

        #make a copy of the list before iterating over it
        up_for_delete_list = list(local_tmp_files)
        #cleanup every entry of this list
        for name in up_for_delete_list:
            cleanup(name, local, remote)

        #remove guard and exit
        cleaning_up_already = False
        return

    import transfer
    out.log('Removing tmp files in namespace ' + namespace, 'cleanup', out.LEVEL_DEBUG)
    #remove remote files first, because there removal might cause local files to happen
    if remote:
        for file in remote_tmp_files[namespace]:
            transfer.remove_remote(file)
            remote_tmp_files[namespace] = []

    #then remove local files
    if local:
        for file in local_tmp_files[namespace]:
            transfer.remove_local(file)
            local_tmp_files[namespace] = []

    #reset namespace list, so it doesn't get cleaned up twice

@out.indent
def cleanup_local():
    out.log('cleaning up local tmp files...', 'engine', out.LEVEL_VERBOSE)
    cleanup(remote = False)

@out.indent
def cleanup_remote():
    out.log('cleaning up remote tmp files...', 'engine', out.LEVEL_VERBOSE)
    cleanup(local = False)

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


def local_is_not_empty(filename):
    if not os.path.isfile(filename):
        return False
    return os.path.getsize(filename) > 0

#returns the name of the local tmp dir. It exists, because it has a .gitignore in it.
def get_local_tmp_dir():
    return LOCAL_TMP_DIR

#returns the name of the remote tmp dir and ensures it exists.
def get_remote_tmp_dir():
    import transfer
    global remote_tmp_dir_created
    if not remote_tmp_dir_created:
        transfer.create_remote_directory(NORM_TMP_DIR, 777)
        remote_tmp_dir_created = True
    return NORM_TMP_DIR

def clean_local_tmp_dir():
    import run
    #create a file, so the removal does not fail
    tmp_file = write_local_file('this file is here to be cleaned up.')
    #unregister it, because it gets wiped by this cleanup already
    unregister_local_file(tmp_file)
    local_tmp_dir = get_local_tmp_dir()
    run.local('rm ' + local_tmp_dir + '/tmp_file_*')

def clean_remote_tmp_dir():
    #import transfer
    import run
    remote_tmp_dir = get_remote_tmp_dir()
    run.remote('rm -f ' + remote_tmp_dir + '/*')

def clean_build_dir():
    import run
    run.local('rm -rf ' + LOCAL_BUILD_DIR)

#registers a new local filename and returns it. Does not actually create the file.
def get_new_local_file(suffix = None, create_file = False):
    import run

    if suffix is None:
        suffix = 'tmp'
    #get filename in tmp dir
    global local_tmp_files
    tmp_dir = get_local_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_').replace('.','_') + '.' + suffix

    #register file in current namespace
    register_local_file(filename)

    if create_file:
        run.local('touch ' + filename)
    
    #return filename
    return filename

#registers a new remote filename and returns it. Does not actually create the file.
def get_new_remote_file(suffix = None):
    if suffix is None:
        suffix = 'tmp'
    #get filenam ein tmp dir
    global remote_tmp_files
    tmp_dir = get_remote_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_').replace('.','_') + '.' + suffix

    #register file in current namespace
    register_remote_file(filename)

    #return file
    return filename

@out.indent
def register_local_file(filename):
    out.log('Registered local tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global local_tmp_files
    global current_tmp_file_namespace
    local_tmp_files[current_tmp_file_namespace].append(filename)

@out.indent
def register_remote_file(filename):
    out.log('Registered remote tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global remote_tmp_files
    global current_tmp_file_namespace
    remote_tmp_files[current_tmp_file_namespace].append(filename)

@out.indent
def unregister_local_file(filename):
    out.log('Unregister local tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global local_tmp_files
    global current_tmp_file_namespace
    local_tmp_files[current_tmp_file_namespace].remove(filename)

@out.indent
def unregister_remote_file(filename):
    out.log('Registered remote tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global remote_tmp_files
    global current_tmp_file_namespace
    remote_tmp_files[current_tmp_file_namespace].remove(filename)



@out.indent
def rename_file(from_file, to_file, file_list):
    out.log('Registered file for renaming ' + from_file + ' -> ' + to_file, 'engine', out.LEVEL_DEBUG)
    global current_tmp_file_namespace
    #define filter function
    def filter(filename):
        if filename == from_file:
            return to_file
        else:
            return filename
    #filter list with that functino
    file_list[current_tmp_file_namespace] = [filter(filename) for filename in file_list[current_tmp_file_namespace]]

def rename_local_file(from_file, to_file):
    return rename_file(from_file, to_file, local_tmp_files)

def rename_remote_file(from_file, to_file):
    return rename_file(from_file, to_file, remote_tmp_files)

#filter constant names: valid constant names contain of only uppercase letters and underscores
def valid_constant(const_name):
    if re.match('(_|[A-Z])+$', const_name):
        return True
    else:
        return False

def add_config(key, value, type='string'):
    import out

    if not valid_constant(key):
        log.out('Not a valid configuration name: ' + key, 'engine', out.LEVEL_ERROR)
        quit()

    if type == 'string':
        escaped_value = "'" + str(value) + "'"
    else:
        escaped_value = str(value)

    assignement = str(key) + " = " + str(escaped_value)

    #write to project config
    filename = PROJECT_CONFIG_FILE
    out.log('PROJECT_CONFIG_FILE is at ' + PROJECT_CONFIG_FILE, 'engine', out.LEVEL_DEBUG)
    file = open(filename, 'a')
    file.write("\n" + assignement + " #added automatically on " + str(datetime.now()) + "\n")
    file.close()

    #make accessible immediately
    globals()[key] = value
    out.log("added " + assignement + " to config", 'engine', out.LEVEL_DEBUG)

#gets a config var 'key', or a dictionary of all config vars if key is not specified.
def get_config(key = None):
    if key is not None:
        if valid_constant(key):
            try:
                value = globals()[key]
                return value
            except KeyError:
                out.log('There is no constant by the name ' + key, 'engine', out.LEVEL_WARNING)
                return None
        else:
            out.log('Not a valid constant name: ' + key, 'engine', out.LEVEL_WARNING)
            return None
    else:
        config_vars = {}
        for k in globals():
            if valid_constant(k):
                config_vars[k] = globals()[k]
        return config_vars


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

def write_local_file(content, suffix = None, permissions = None, filename = None):
    if permissions is not None:
        out.log('Error: Setting permissions in write_local_file is not implemented yet.', 'engine', out.LEVEL_ERROR)
    if filename is None:
        filename = get_new_local_file(suffix)
    if isinstance(content, str):
        content = unicode(content, 'utf-8' )
    file = open(filename, 'w', encoding='utf-8')
    file.write(content)
    file.close()
    return filename

def write_remote_file(content, suffix = None, permissions = None, filename = None):
    import transfer
    local_file = write_local_file(content, suffix)
    if filename is None:
        remote_file = get_new_remote_file(suffix)
    else:
        remote_file = filename
    transfer.put(local_file, remote_file, permissions = permissions)
    return remote_file

def read_local_file(filename):
    file = open(filename, 'r', encoding='utf-8')
    data = file.read()
    file.close()
    return data

def read_remote_file(filename):
    import transfer
    local_file = transfer.get(filename)
    return read_local_file(local_file)

@out.indent
def get_remote_www_dir_abspath():
    import run
    out.log('getting absolute remote path of www directory', 'engine')
    filename = get_new_remote_file('out')
    run.remote('pwd >' + filename)
    return read_remote_file(filename).rstrip()

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


def md5sum(filename):
    md5 = hashlib.md5()
    with open(os.path.join(LOCAL_WWW_DIR, filename), 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

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

def get_all_directories(file_list):
    dir_list = []
    for file in file_list:
        directory = os.path.dirname(file)
        while not directory in dir_list:
            dir_list.append(directory)
            directory = os.path.dirname(directory)
    #sort by length of dir, so directory dependencies get resolved correctly
    dir_list.sort(lambda x,y: cmp(len(x), len(y)))
    return dir_list
