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

current_tmp_file_namespace = 'global'

#remember the files we have created for cleaning up later
local_tmp_files = {}
local_tmp_files['global'] = []
remote_tmp_files = {}
remote_tmp_files['global'] = []


def get_random_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def get_random_secury_id():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

#decorator for preparation and cleanup
def prepare_and_clean(func):
    def decorated_func(*args, **kwargs):
        result = func(*args, **kwargs)
        cleanup()
        return result
    return decorated_func

#decorator for cleaning up immediately
def cleanup_immediately(func):
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
def get_new_local_file():
    #get filename in tmp dir
    global local_tmp_files
    tmp_dir = get_local_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.tmp'

    #register file in current namespace
    global current_tmp_file_namespace
    local_tmp_files[current_tmp_file_namespace].append(filename)
    
    #return filename
    return filename

#registers a new remote filename and returns it. Does not actually create the file.
def get_new_remote_file():
    #get filenam ein tmp dir
    global remote_tmp_files
    tmp_dir = get_remote_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.tmp'

    #register file in current namespace
    global current_tmp_file_namespace
    remote_tmp_files[current_tmp_file_namespace].append(filename)

    #return file
    return filename

#writes a database dump to file and returns its name
def create_remote_dump():
    import run
    filename = get_new_remote_file()
    run.remote(REMOTE_MYSQLDUMP_CMD + ' >' + filename)
    return filename

#truncates the remote db by executing some sql (truncation leaves the db empty, but it still exists)
def truncate_local_db():
    import mysql
    mysql.execute_local_statement(TRUNCATE_LOCAL_DB_SQL)

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

