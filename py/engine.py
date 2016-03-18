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

import run
import transfer

#count here
local_tmp_files = []
remote_tmp_files = []

#decorator for preparation and cleanup
def prepare_and_clean(func):
    def decorated_func(**kwargs):
        func(**kwargs)
        cleanup()
    return decorated_func

#cleanup is being run at the very end. cleans up all the files that have been created in the process.
def cleanup():
    for file in local_tmp_files:
        run.local('rm ' + file)
    for file in remote_tmp_files:
        run.remote('rm ' + file)

#returns the name of the local tmp dir. It exists, because it has a .gitignore in it.
def get_local_tmp_dir():
    return LOCAL_TMP_DIR

#returns the name of the remote tmp dir and ensures it exists.
def get_remote_tmp_dir():
    return REMOTE_TMP_DIR

#registers a new local filename and returns it. Does not actually create the file.
def get_new_local_file():
    global local_tmp_files
    tmp_dir = get_local_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.tmp'
    local_tmp_files.append(filename)
    return filename

#registers a new remote filename and returns it. Does not actually create the file.
def get_new_remote_file():
    global remote_tmp_files
    tmp_dir = get_remote_tmp_dir()
    filename = tmp_dir + '/tmp_file_' + str(datetime.now()).replace(' ', '_') + '.tmp'
    remote_tmp_files.append(filename)
    return filename

#writes a database dump to file and returns its name
def create_remote_dump():
    filename = get_new_remote_file()
    run.remote(REMOTE_MYSQLDUMP_CMD + ' >' + filename)
    return filename

#truncates the remote db by executing some sql (truncation leaves the db empty, but it still exists)
def truncate_local_db():
    execute_local_mysql(TRUNCATE_LOCAL_DB_SQL)

def write_local_file(content):
    filename = get_new_local_file()
    file = open(filename, 'w')
    file.write(content)
    file.close()
    return filename

def write_remote_file(content):
    local_file = write_local_file(content)
    remote_file = transfer.put(local_file)
    return remote_file

#executes a mysql file locally
def execute_local_mysql_file(filename):
    run.local(LOCAL_MYSQL_CMD + '<' + filename)

#executes a mysql statement locally. This is done by writing a mysql file and then pass it to the mysql client via cli.
def execute_local_mysql(statement):
    filename = write_local_file(statement)
    execute_local_mysql_file(filename)
