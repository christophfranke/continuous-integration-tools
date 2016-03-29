import os
from constants import *

#issue some warning if something goes wrong, so the user always knows exactly how to solve a problem
def const_warning(const_name, const_dependency):
    print "Warning: " + const_name + " could not be assembled by script. Make sure you have " + const_dependency + " set in your project config."

def const_subsequent(const_name, const_dependency):
    print "Warning: " + const_name + " could not be assembled, because " + const_dependency + " could not be assembled. See the above warnings on what config is missing to assemble " + const_dependency


#set some vars that have no dependency at all
CONFIG_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
PROJECT_CONFIG_FILE = os.path.abspath(CONFIG_DIR + '/../../project_config.py')
SCRIPT_DIR = os.path.abspath(CONFIG_DIR + '/..')
FAB_FILE = SCRIPT_DIR + '/fabfile.py'


#import default configs first
from config_default import *
from project_config_default import *

#import global config
try:
    from config_global import *
except ImportError:
    #look for global config in home directory
    HOME_DIR = os.path.expanduser('~')
    GLOBAL_CONFIG_FILE = os.path.abspath(HOME_DIR + '/.deploy-tools/config.py')
    #ok, there is one
    if os.path.isfile(GLOBAL_CONFIG_FILE):
        #create symlink to global config file
        os.system('cd ' + CONFIG_DIR + ' && ln -s ' + GLOBAL_CONFIG_FILE + ' config_global.py')
        #import symlink
        from config_global import *


#then try to import project configs in project folder
try:
    from project_config import *
except ImportError:
    print "Warning: No Project Config Found. The project config is expected to be at " + os.path.abspath(CONFIG_DIR + '/../../project_config.py')


#local directories
LOCAL_ROOT_DIR = os.path.abspath(SCRIPT_DIR + '/' + RELATIVE_LOCAL_PROJECT_ROOT)
LOCAL_WWW_DIR = os.path.abspath(LOCAL_ROOT_DIR + '/' + WWW_DIR)
LOCAL_DB_DIR = os.path.abspath(LOCAL_ROOT_DIR + '/' + DB_DIR)
LOCAL_TMP_DIR = os.path.abspath(SCRIPT_DIR + '/tmp')
LOCAL_TAR_DIR = os.path.abspath(LOCAL_TMP_DIR + '/tar')

if OUTPUT_LOG_FILE is not None:
    LOG_FILE = os.path.abspath(SCRIPT_DIR + '/' + OUTPUT_LOG_FILE)
else:
    LOG_FILE = None

LOCAL_MD5_TABLE_FILE = os.path.abspath(LOCAL_ROOT_DIR + '/' + MD5_TABLE_FILE)


try:
    LOCAL_HTTP_ROOT
    print "Warning: LOCAL_HTTP_ROOT is deprecated. Use LOCAL_DOMAIN instead (and omit the http:// there)."
except NameError:
    try:
        LOCAL_ROOT_URL = 'http://' + LOCAL_DOMAIN
    except:
        LOCAL_ROOT_URL = None
        const_warning('LOCAL_ROOT_URL', 'LOCAL_DOMAIN')


#remote directories
try:
    REMOTE_ROOT_URL = 'http://' + LIVE_DOMAIN
except:
    const_warning('REMOTE_ROOT_URL', 'LIVE_DOMAIN')
    REMOTE_ROOT_URL = None

if REMOTE_ROOT_DIR is None:
    REMOTE_WWW_DIR = '.'
    REMOTE_TMP_DIR = TMP_DIR
else:
    REMOTE_WWW_DIR = os.path.normpath(REMOTE_ROOT_DIR + '/' + WWW_DIR)
    REMOTE_TMP_DIR = os.path.normpath(REMOTE_ROOT_DIR + '/' + TMP_DIR)


#concatenate mysql command strings. Really useful stuff...
try:
    LOCAL_MYSQL_CMD = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '
    LOCAL_MYSQLDUMP_CMD = 'mysqldump -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '
    LOCAL_MYSQL_NO_DB_CMD = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' '
except:
    print "Warning: LOCAL_MYSQL_CMD, LOCAL_MYSLQDUMP_CMD and LOCAL_MYSQL_NO_DB_CMD could not be assembled by script. Make sure you have LOCAL_DB_USER, LOCAL_DB_PASSWORD and LOCAL_DB_NAME set in your project config."

try:
    REMOTE_MYSQL_PARAMS = ' -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD + ' --host=' + REMOTE_DB_HOST + ' '
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

    REMOTE_MYSQL_CMD = 'mysql' + REMOTE_MYSQL_PARAMS
    REMOTE_MYSQLDUMP_CMD = 'mysqldump' + REMOTE_MYSQL_PARAMS
except:
    print "Warning: REMOTE_MYSQL_CMD and REMOTE_MYSLQDUMP_CMD could not be assembled by script. Make sure you have REMOTE_DB_USER, REMOTE_DB_PASSWORD and REMOTE_DB_NAME set in your project config."


#some standard mysql commands
try:
    TRUNCATE_LOCAL_DB_SQL = 'DROP DATABASE `' + LOCAL_DB_NAME + '`;CREATE DATABASE `' + LOCAL_DB_NAME + '`;'
except:
    const_warning('TRUNCATE_LOCAL_DB_SQL', 'LOCAL_DB_NAME')
try:
    TRUNCATE_REMOTE_DB_SQL = 'DROP DATABASE `' + REMOTE_DB_NAME + '`;CREATE DATABASE `' + REMOTE_DB_NAME + '`;'
except:
    const_warning('TRUNCATE_REMOTE_DB_SQL', 'REMOTE_DB_NAME')


try:
    if ENABLE_BUILD_SYSTEM:
        RELATIVE_SRC_DIR = WWW_DIR + '/' + SRC_URL
        RELATIVE_BUILD_DIR = WWW_DIR + '/' + BUILD_URL

        LOCAL_SRC_DIR = os.path.abspath(LOCAL_ROOT_DIR + '/' + RELATIVE_SRC_DIR)
        LOCAL_BUILD_DIR = os.path.abspath(LOCAL_ROOT_DIR + '/' + RELATIVE_BUILD_DIR)

        if REMOTE_ROOT_DIR is None:
            REMOTE_BUILD_DIR = BUILD_URL
        else:
            REMOTE_BUILD_DIR = os.path.normpath(REMOTE_ROOT_DIR + '/' + RELATIVE_BUILD_DIR)

        LOCAL_MAKE_DIR = os.path.abspath(SCRIPT_DIR + '/make')

        MAKEFILE_VARS = 'SRC=' + LOCAL_SRC_DIR + ' BUILD=' + LOCAL_BUILD_DIR + ' SRC_URL=' + SRC_URL + ' BUILD_URL=' + BUILD_URL + ' WWW_DIR=' + LOCAL_WWW_DIR
except:
    print "Build related variables could not be assembled. Make sure you have set SCR_URL and BUILD_URL in your project config."


#wordpress specifics
if IS_WORDPRESS:
    if WP_DIR == '':
        WP_DIR = WWW_DIR
    LOCAL_WP_DIR = os.path.abspath(LOCAL_ROOT_DIR + '/' + WP_DIR)
    if REMOTE_ROOT_DIR is None:
        REMOTE_WP_DIR = WP_DIR
    else:
        REMOTE_WP_DIR = os.path.normpath(REMOTE_ROOT_DIR + '/' + WP_DIR)

#ssh or ftp?
if TRANSFER_SYSTEM == '':
    TRANSFER_SYSTEM = 'FTP' #workaround: always fallback to ftp. later on, we will use ssh again

#ssh or php
if COMMAND_SYSTEM == '':
    COMMAND_SYSTEM = 'PHP' #also workaround: use php command system for now. later on we will support ssh


if TRANSFER_SYSTEM == 'FTP':
    if FTP_HOST == '':
        try:
            FTP_HOST = LIVE_DOMAIN
        except:
            const_warning('FTP_HOST', 'LIVE_DOMAIN')

    try:
        UNUSED_FTP_COMMAND_BETTER_TRY_NOW_AND_WARN_THAN_FAIL_LATER_SILENTLY = 'ftp -i ftp://' + FTP_USER + ':' + FTP_PASSWORD + '@' + FTP_HOST
    except:
        print "Warning: You have set the TRANSFER_SYSTEM to 'FTP', but the variables FTP_USER, FTP_PASSWORD and FTP_HOST are not set correctly. Make sure you have these variables set in your project config. The transfer system will not work."


if COMMAND_SYSTEM == 'PHP':
    if REMOTE_ROOT_URL is not None:
        try:
            REMOTE_COMMAND_FILE = os.path.normpath(REMOTE_WWW_DIR + '/' + SECURITY_HASH + '.php')
            REMOTE_COMMAND_URL = REMOTE_ROOT_URL + '/' + SECURITY_HASH + '.php'
        except:
            pass
    else:
        const_subsequent('REMOTE_COMMAND_FILE', 'REMOTE_ROOT_URL')

