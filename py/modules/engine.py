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

current_tmp_file_namespace = 'global'
cleaning_up_already = False

#remember the files we have created for cleaning up later
local_tmp_files = {}
local_tmp_files['global'] = []
remote_tmp_files = {}
remote_tmp_files['global'] = []

start_time = time.time()

def get_random_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def get_random_secury_id():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))

#decorator for preparation and cleanup
def prepare_and_clean(func):
    def decorated_func(*args, **kwargs):
        import run
        import transfer
        import out
        global start_time
        start_time = time.time()
        out.clear_logfile()
        global COMMAND_SYSTEM_READY
        if not COMMAND_SYSTEM_READY:
            initialize()
        result = func(*args, **kwargs)
        cleanup()
        elapsed_time = "{:.3f}".format(time.time() - start_time)
        out.log('Done. Took ' + elapsed_time + ' seconds.')
        return result
    return out.indent(decorated_func)

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

@out.indent
def initialize():
    import transfer
    import run
    transfer.create_remote_directory(NORM_TMP_DIR, 777)
    run.upload_command_file()
    global COMMAND_SYSTEM_READY
    if not COMMAND_SYSTEM_READY:
        add_config('COMMAND_SYSTEM_READY', True, 'Boolean')


#cleanup is being run at the very end. cleans up all the files that have been created in the process.
@out.indent
def cleanup(namespace = None):
    #cleanup all namespaces
    if namespace is None:
        #guard for unwanted recursion
        global cleaning_up_already
        if cleaning_up_already:
            return
        cleaning_up_already = True

        #make a copy of the list before iterating over it
        up_for_delete_list = list(local_tmp_files)
        #cleanup every entry of this list
        for name in up_for_delete_list:
            cleanup(name)

        #remove guard and exit
        cleaning_up_already = False
        return

    import transfer
    out.log('Removing tmp files in namespace ' + namespace, 'cleanup', out.LEVEL_DEBUG)
    #remove remote files first, because there removal might cause local files to happen
    for file in remote_tmp_files[namespace]:
        transfer.remove_remote(file)
    #then remove local files
    for file in local_tmp_files[namespace]:
        transfer.remove_local(file)

    #reset namespace list, so it doesn't get cleaned up twice
    remote_tmp_files[namespace] = []
    local_tmp_files[namespace] = []


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
    cleanup()
    out.log('Exited with errors. Look at output/output.log for a detailed log.', 'engine', out.LEVEL_ERROR)
    exit()


def local_is_not_empty(filename):
    if not os.path.isfile(filename):
        return False
    return os.path.getsize(filename) > 0

#returns the name of the local tmp dir. It exists, because it has a .gitignore in it.
def get_local_tmp_dir():
    return LOCAL_TMP_DIR

#returns the name of the remote tmp dir and ensures it exists.
def get_remote_tmp_dir():
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
    run.remote('rm ' + remote_tmp_dir + '/tmp_file_*')

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


def get_database_dump_file(compression = False):
    import run
    #mysql dump filenames
    if not os.path.isdir(LOCAL_DB_DIR):
        run.local('mkdir -p ' + LOCAL_DB_DIR)
    filename = os.path.abspath(LOCAL_DB_DIR + '/dump-' + str(datetime.now()).replace(' ', '-') + '.sql')
    if compression:
        filename += '.gz'
    return filename


def write_local_file(content, suffix = None, permissions = None):
    if permissions is not None:
        out.log('Error: Setting permissions in write_local_file is not implemented yet.', 'engine', out.LEVEL_ERROR)
    filename = get_new_local_file(suffix)
    file = open(filename, 'w')
    file.write(content)
    file.close()
    return filename

def write_remote_file(content, suffix = None, permissions = None):
    import transfer
    local_file = write_local_file(content, suffix)
    remote_file = get_new_remote_file(suffix)
    transfer.put(local_file, remote_file, permissions = permissions)
    return remote_file

