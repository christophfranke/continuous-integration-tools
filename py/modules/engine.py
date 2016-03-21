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
        global COMMAND_SYSTEM_READY
        if not COMMAND_SYSTEM_READY:
            run.upload_command_file()
            COMMAND_SYSTEM_READY = True
        result = func(*args, **kwargs)
        cleanup()
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


#cleanup is being run at the very end. cleans up all the files that have been created in the process.
def cleanup(namespace = None):
    import transfer
    if namespace is None:
        namespace = 'global'
    #remove remote files first, because there removal might cause local files to happen
    for file in remote_tmp_files[namespace]:
        transfer.remove_remote(file)
    #then remove local files
    for file in local_tmp_files[namespace]:
        transfer.remove_local(file)


#returns the name of the local tmp dir. It exists, because it has a .gitignore in it.
def get_local_tmp_dir():
    return LOCAL_TMP_DIR

#returns the name of the remote tmp dir and ensures it exists.
def get_remote_tmp_dir():
    return REMOTE_TMP_DIR

#registers a new local filename and returns it. Does not actually create the file.
def get_new_local_file(suffix = 'tmp'):
    #get filename in tmp dir
    global local_tmp_files
    tmp_dir = get_local_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.' + suffix

    #register file in current namespace
    global current_tmp_file_namespace
    local_tmp_files[current_tmp_file_namespace].append(filename)
    
    #return filename
    return filename

#registers a new remote filename and returns it. Does not actually create the file.
def get_new_remote_file(suffix = 'tmp'):
    #get filenam ein tmp dir
    global remote_tmp_files
    tmp_dir = get_remote_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.' + suffix

    #register file in current namespace
    global current_tmp_file_namespace
    remote_tmp_files[current_tmp_file_namespace].append(filename)

    #return file
    return filename

def add_config(key, value):
    import out

    #write to project config
    filename = PROJECT_CONFIG_FILE
    out.log('PROJECT_CONFIG_FILE is at ' + PROJECT_CONFIG_FILE, out.LEVEL_DEBUG)
    file = open(filename, 'a')
    file.write("\n" + key + " = '" + value + "' #added automatically on " + str(datetime.now()) + "\n")
    file.close()

    #make accessible immediately
    globals()[key] = value
    out.log("added " + key + " = " + value + " to config", out.LEVEL_DEBUG)

def get_database_dump_file(compression = False):
    import run
    #mysql dump filenames
    if not os.path.isdir(LOCAL_DB_DIR):
        run.local('mkdir -p ' + LOCAL_DB_DIR)
    filename = os.path.abspath(LOCAL_DB_DIR + '/dump-' + str(datetime.now()).replace(' ', '-') + '.sql')
    if compression:
        filename += '.gz'
    return filename


def write_local_file(content):
    filename = get_new_local_file()
    file = open(filename, 'w')
    file.write(content)
    file.close()
    return filename

def write_remote_file(content):
    import transfer
    local_file = write_local_file(content)
    remote_file = transfer.put(local_file)
    return remote_file
