#import all constants
try:
    #this import will work when we are in scripts folder
    from config.config import *
except ImportError:
    try:
        #this will work form other places (relative import)
        from ...config.config import *
    except ImportError:
        #we are out of luck...
        print "Could not import config package. Try navigating to script folder before starting the script."
        exit()

import random
import string
from datetime import datetime

import out

current_tmp_file_namespace = 'global'

#remember the files we have created for cleaning up later
local_tmp_files = {}
local_tmp_files['global'] = []
remote_tmp_files = {}
remote_tmp_files['global'] = []


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
        out.clear_logfile()
        global COMMAND_SYSTEM_READY
        if not COMMAND_SYSTEM_READY:
            transfer.create_remote_directory(REMOTE_TMP_DIR, 777)
            run.upload_command_file()
            add_config('COMMAND_SYSTEM_READY', 'True', 'Boolean')
        result = func(*args, **kwargs)
        cleanup()
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


#cleanup is being run at the very end. cleans up all the files that have been created in the process.
@out.indent
def cleanup(namespace = None):
    import transfer
    if namespace is None:
        namespace = 'global'
    out.log('Removing tmp files in namespace ' + namespace, 'cleanup', out.LEVEL_DEBUG)
    #remove remote files first, because there removal might cause local files to happen
    for file in remote_tmp_files[namespace]:
        transfer.remove_remote(file)
    #then remove local files
    for file in local_tmp_files[namespace]:
        transfer.remove_local(file)

    #reset list
    remote_tmp_files[namespace] = []
    local_tmp_files[namespace] = []


def get_suffix(filename):
    #find the last dot in filename
    pos = filename.rfind('.')

    #this file has no suffix
    if pos == -1:
        return None
    else:
        #return suffix
        return filename[pos+1:]


def local_is_not_empty(filename):
    if not os.path.isfile(filename):
        return False
    return os.path.getsize(filename) > 0

#returns the name of the local tmp dir. It exists, because it has a .gitignore in it.
def get_local_tmp_dir():
    return LOCAL_TMP_DIR

#returns the name of the remote tmp dir and ensures it exists.
def get_remote_tmp_dir():
    return REMOTE_TMP_DIR

def clean_local_tmp_dir():
    import run
    local_tmp_dir = get_local_tmp_dir()
    run.local('rm ' + local_tmp_dir + '/tmp_file_*')

def clean_remote_tmp_dir():
    #import transfer
    import run
    remote_tmp_dir = get_remote_tmp_dir()
    #command = 'remove ' + remote_tmp_dir + '/tmp_file_*'
    #transfer.execute_ftp_command(command)
    run.remote('rm ' + remote_tmp_dir + '/tmp_file_*')


#registers a new local filename and returns it. Does not actually create the file.
def get_new_local_file(suffix = None, create_file = False):
    import run

    if suffix is None:
        suffix = 'tmp'
    #get filename in tmp dir
    global local_tmp_files
    tmp_dir = get_local_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.' + suffix

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
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.' + suffix

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

def compile_mo_files():

    files = []
    for root, dirnames, filenames in os.walk(LOCAL_WWW_DIR):
        for filename in fnmatch.filter(filenames, '*.po'):
            files.append(os.path.join(root, filename))

    for po in files:
        mo = po[:-3] + '.mo'
        # needs to be refreshed if
        # 1. there is no .mo file
        # 2. the .mo file is out of date
        # 3. the .mo file is not placed in a folder named 'orig'
        if (not os.path.isfile(mo) or os.path.getmtime(po) > os.path.getmtime(mo)) and (not os.path.split(os.path.dirname(po))[1] == 'orig'):
            local('msgfmt -o ' + mo + ' ' + po)
 
def add_config(key, value, type='string'):
    import out

    if type == 'string':
        escaped_value = "'" + value + "'"
    else:
        escaped_value = value

    #write to project config
    filename = PROJECT_CONFIG_FILE
    out.log('PROJECT_CONFIG_FILE is at ' + PROJECT_CONFIG_FILE, 'engine', out.LEVEL_DEBUG)
    file = open(filename, 'a')
    file.write("\n" + key + " = " + escaped_value + " #added automatically on " + str(datetime.now()) + "\n")
    file.close()

    #make accessible immediately
    globals()[key] = value
    out.log("added " + key + " = " + value + " to config", 'engine', out.LEVEL_DEBUG)

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

