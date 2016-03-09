#this file contains all the functions, that are not really useful from the fab interface, but are needed by the functions in those files. Also, to hide them form the interface, they get thrown in a namespace
from constants import *
from fabric.api import local, put, get, env, run, cd, lcd


#executes a mysql file on the remote
def execute_file_remote(filename):
    put(filename, TMP_SQL_FILE)
    run(REMOTE_MYSQL + '<' + TMP_SQL_FILE)
    run('rm ' + TMP_SQL_FILE)

#executes a mysql file locally
def execute_file_local(filename):
    local(LOCAL_MYSQL + '<' + filename)

#executes a mysql statement locally
def execute_mysql_local(statement):
    file = open(TMP_SQL_FILE, 'w')
    file.write(statement)
    file.close()
    execute_file_local(TMP_SQL_FILE)
    local('rm ' + TMP_SQL_FILE)

def execute_mysql_local_no_db(statement):
    file = open(TMP_SQL_FILE, 'w')
    file.write(statement)
    file.close()
    local(LOCAL_MYSQL_NO_DB + '<' + TMP_SQL_FILE)
    local('rm ' + TMP_SQL_FILE)

#executes a mysql statement remotely
def execute_mysql_remote(statement):
    file = open(TMP_SQL_FILE, 'w')
    file.write(statement)
    file.close()
    execute_file_remote(TMP_SQL_FILE)
    local('rm ' + TMP_SQL_FILE)

#creates the tmp dirs locally and on the remote
def create_tmp_dirs():
    local('mkdir -p ' + FABRIC_TMP_DIR)
    run('mkdir -p ' + FABRIC_TMP_DIR)

#removes all the tmp dirs created by create_tmp_dirs
def remove_tmp_dirs():
    local('rm -rf ' + FABRIC_TMP_DIR)
    run('rm -rf ' + FABRIC_TMP_DIR)

#takes a database dump file and puts it in the remote database. also makes a backup before and removes the content of the remote datebase.
def upload_file_to_remote_db(filename):
    #backup db first
    backup_db()
    #compress file
    TAR_FILENAME = filename + '.tar.gz'
    local('tar -zcf ' + TAR_FILENAME + ' ' + filename)
    #upload file
    put(TAR_FILENAME, UPLOAD_FILE_TO_REMOTE_FILENAME_GZ)
    #uncompress on remote
    run('tar -zxf ' + UPLOAD_FILE_TO_REMOTE_FILENAME_GZ)
    run('mv ' + filename + ' ' + UPLOAD_FILE_TO_REMOTE_FILENAME)
    #truncate db
    execute_mysql_remote(TRUNCATE_REMOTE_DB_SQL)
    #import file
    run(REMOTE_MYSQL + '<' + UPLOAD_FILE_TO_REMOTE_FILENAME)
    #cleanup
    run('rm ' + UPLOAD_FILE_TO_REMOTE_FILENAME)

#makes a backup of the remote db. A filename can be specified. The standard filename contains a timestamp
def backup_db(filename=SQL_GZ_DUMP_FILE):
    #create tmp dir
    run('mkdir -p ' + FABRIC_TMP_DIR)
    with cd(FABRIC_TMP_DIR):
        #export
        run(REMOTE_MYSQLDUMP + '>dump.sql')
        #compress before downloading
        run('tar -acf dump.tar.gz dump.sql')
    #download
    get(FABRIC_TMP_DIR + '/dump.tar.gz', filename)
    #cleanup
    run('rm -rf ' + FABRIC_TMP_DIR)

def ask_user(question, hint='[y/n]'):
    value = raw_input(question + ' ' + hint + ': ')
    return value.lower() == 'y'


