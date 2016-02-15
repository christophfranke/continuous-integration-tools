#import datetime for timestamp constant
from datetime import datetime

#in case of a constant set in multiple config files, the latest import counts.

#import example configs first
from config_example import *
from project_config_example import *

#then try to import project configs in project folder
try:
    from project_config import *
except ImportError:
    pass

#finally, try to get config.py file in this folder
try:
    from config import *
except ImportError:
    pass


#now we should have the configuration ready to setup all the constants we need

SCRIPT_FILE = __file__
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

try:
    RELATIVE_LOCAL_PROJECT_ROOT
except NameError:
    RELATIVE_LOCAL_PROJECT_ROOT = '..'

LOCAL_ROOT_FOLDER = SCRIPT_DIR + '/' + RELATIVE_LOCAL_PROJECT_ROOT
LOCAL_WWW_FOLDER = LOCAL_ROOT_FOLDER + '/' + WWW_FOLDER

try:
    DB_FOLDER
except NameError:
    DB_FOLDER = LOCAL_ROOT_FOLDER + '/Datenbank'

SQL_DUMP_FILE = DB_FOLDER + '/dump-' + str(datetime.now()).replace(' ', '-') + '.sql'
SQL_GZ_DUMP_FILE = SQL_DUMP_FILE + '.gz'


REMOTE_WWW_FOLDER = REMOTE_ROOT_FOLDER + '/' + WWW_FOLDER

LOCAL_MYSQL = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '
LOCAL_MYSQLDUMP = 'mysqldump -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '

#concatenate mysql command strings
REMOTE_MYSQL_PARAMS = ' -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD + ' '
try:
    REMOTE_DB_PORT
    REMOTE_MYSQL_PARAMS += '--port=' + REMOTE_DB_PORT + ' '
except NameError:
    pass
try:
    REMOTE_DB_SOCKET
    REMOTE_MYSQL_PARAMS += '--socket=' + REMOTE_DB_SOCKET + ' '
except NameError:
    pass
REMOTE_MYSQL_PARAMS += REMOTE_DB_NAME + ' '

REMOTE_MYSQL = 'mysql' + REMOTE_MYSQL_PARAMS
REMOTE_MYSQLDUMP = 'mysqldump' + REMOTE_MYSQL_PARAMS

FABRIC_TMP_DIR = 'fabric-tmp-dir'
TMP_SQL_FILE = 'fabric-tmp.sql'
SSH_TMP_FILE = FABRIC_TMP_DIR + '/ssh-key-tmp-file'

try:
    RELATIVE_SRC_DIR = WWW_FOLDER + '/' + SRC_URL
    RELATIVE_BUILD_DIR = WWW_FOLDER + '/' + BUILD_URL

    SRC_DIR = LOCAL_ROOT_FOLDER + '/' + RELATIVE_SRC_DIR
    BUILD_DIR = LOCAL_ROOT_FOLDER + '/' + RELATIVE_BUILD_DIR

    REMOTE_BUILD_DIR = REMOTE_ROOT_FOLDER + '/' + RELATIVE_BUILD_DIR

    MAKEFILE_VARS = 'SRC=' + SRC_DIR + ' BUILD=' + BUILD_DIR + ' SRC_URL=' + SRC_URL + ' BUILD_URL=' + BUILD_URL + ' WWW_FOLDER=' + LOCAL_WWW_FOLDER
except:
    pass

try:
    GIT_CURRENT_BRANCH = GIT_BRANCH
except:
    GIT_CURRENT_BRANCH = '' #default to no specific branch


try:
    LOCAL_WP_FOLDER = LOCAL_ROOT_FOLDER + '/' + WP_FOLDER
    REMOTE_WP_FOLDER = REMOTE_ROOT_FOLDER + '/' + WP_FOLDER
except:
    LOCAL_WP_FOLDER = LOCAL_WWW_FOLDER
    REMOTE_WP_FOLDER = REMOTE_WWW_FOLDER

try:
    WP_FOLDER
except:
    WP_FOLDER = WWW_FOLDER



TRUNCATE_LOCAL_DB_SQL = 'DROP DATABASE `' + LOCAL_DB_NAME + '`;CREATE DATABASE `' + LOCAL_DB_NAME + '`;'
TRUNCATE_REMOTE_DB_SQL = 'DROP DATABASE `' + REMOTE_DB_NAME + '`;CREATE DATABASE `' + REMOTE_DB_NAME + '`;'

