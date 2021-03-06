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

#
try:
    WWW_FOLDER
    print "Warning: WWW_FOLDER is deprecated. Use WWW_DIR instead."
    if WWW_FOLDER is not None and WWW_DIR is None:
        WWW_DIR = WWW_FOLDER
        print "Warning: WWW_DIR has been set to the value of WWW_FOLDER. This has been made for legacy reasons. Please remove the WWW_FOLDER from your project config and use WWW_DIR instead."
except NameError:
    #no WWW_FOLDER, no problem
    pass

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

LOCAL_MD5_TABLE_FILE = os.path.abspath(LOCAL_ROOT_DIR + '/' + DEPLOYED_MD5_TABLE_FILE)


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

try:
    #if remote root folder does not throw a NameError, we have to warn about deprecated configuration.
    REMOTE_ROOT_FOLDER
    print "Warning: REMOTE_ROOT_FOLDER is deprecated. Use FTP_PATH_TO_WWW_DIR or SSH_PATH_TO_WWW_DIR instead. Note, that these constants have a different meaning."
except NameError:
    #REMOTE_ROOT_FOLDER resulted in a NameError, that means the project_config is correct, nothing to do.
    pass

try:
    #if remote root folder does not throw a NameError, we have to warn about deprecated configuration.
    REMOTE_ROOT_DIR
    print "Warning: REMOTE_ROOT_DIR is deprecated. Use FTP_PATH_TO_WWW_DIR or SSH_PATH_TO_WWW_DIR instead. Note, that these constants have a different meaning."
except NameError:
    #REMOTE_ROOT_DIR resulted in a NameError, that means the project_config is correct, nothing to do.
    pass


NORM_WWW_DIR = '.'
NORM_TMP_DIR = os.path.normpath(TMP_DIR)

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


if ENABLE_BUILD_SYSTEM:
    try:
        #assemble local build variables
        LOCAL_SRC_DIR = os.path.abspath(LOCAL_ROOT_DIR + '/' + WWW_DIR + '/' + SRC_URL)
        LOCAL_BUILD_DIR = os.path.abspath(LOCAL_ROOT_DIR + '/' + WWW_DIR + '/' + BUILD_URL)

        LOCAL_MAKE_DIR = os.path.abspath(SCRIPT_DIR + '/make')

        MAKEFILE_VARS = 'SRC=' + LOCAL_SRC_DIR + ' BUILD=' + LOCAL_BUILD_DIR + ' SRC_URL=' + SRC_URL + ' BUILD_URL=' + BUILD_URL + ' WWW_DIR=' + LOCAL_WWW_DIR

        NORM_SRC_DIR = os.path.normpath(SRC_URL)
        NORM_BUILD_DIR = os.path.normpath(BUILD_URL)

    except:
        print "Local build related variables could not be assembled. Make sure you have set SCR_URL and BUILD_URL in your project config."


#wordpress specifics
if IS_WORDPRESS:
    LOCAL_WP_DIR = os.path.abspath(LOCAL_WWW_DIR + '/' + WP_DIR)

    NORM_WP_DIR = os.path.normpath(WP_DIR)

#ssh or ftp?
if TRANSFER_SYSTEM == '':
    TRANSFER_SYSTEM = 'FTP' #workaround: always fallback to ftp. later on, we will use ssh again, or maybe sftp

#ssh or php
if COMMAND_SYSTEM == '':
    COMMAND_SYSTEM = 'PHP' #also workaround: use php command system for now. later on we will support ssh

if TRANSFER_SYSTEM == 'FTP':
    try:
        FTP_WWW_DIR = os.path.normpath(FTP_PATH_TO_WWW_DIR)
    except:
        const_warning('FTP_WWW_DIR', 'FTP_PATH_TO_WWW_DIR')

if TRANSFER_SYSTEM == 'SSH' or COMMAND_SYSTEM == 'SSH':
    try:
        SSH_WWW_DIR = os.path.normpath(SSH_PATH_TO_WWW_DIR)
    except:
        const_warning('SSH_WWW_DIR', 'SSH_PATH_TO_WWW_DIR')


if TRANSFER_SYSTEM == 'FTP':
    if FTP_HOST == '':
        try:
            FTP_HOST = LIVE_DOMAIN
        except:
            const_warning('FTP_HOST', 'LIVE_DOMAIN')

    try:
        UNUSED_FTP_COMMAND_BETTER_TRY_NOW_AND_WARN_THAN_FAIL_LATER_SILENTLY = 'ftp -i ' + FTP_PROTOCOL + '://' + FTP_USER + ':' + FTP_PASSWORD + '@' + FTP_HOST
    except:
        print "Warning: You have set the TRANSFER_SYSTEM to 'FTP', but the variables FTP_USER, FTP_PASSWORD and FTP_HOST are not set correctly. Make sure you have these variables set in your project config. The transfer system will not work."


if REMOTE_ROOT_URL is not None:
    try:
        REMOTE_COMMAND_URL = REMOTE_ROOT_URL + '/' + SECURITY_HASH + COMMAND_FILE_SUFFIX
        NORM_COMMAND_FILE = os.path.normpath(SECURITY_HASH + COMMAND_FILE_SUFFIX)
    except:
        if COMMAND_SYSTEM == 'PHP':
            const_warning('REMOTE_COMMAND_URL', 'SECURITY_HASH')
            const_warning('NORM_COMMAND_FILE', 'SECURITY_HASH')
else:
    const_subsequent('REMOTE_COMMAND_URL', 'REMOTE_ROOT_URL')


def replace_first_slash(s):
    if s[0] == '/':
        return '^/?' + s[1:]
    else:
        return s

#don't fail to assemble the regex when the command url is not set, because that would break execution completely (which is not what we want obviously).
try:
    COMMAND_URL_FOR_REGEX = SECURITY_HASH + COMMAND_FILE_SUFFIX
except NameError:
    COMMAND_URL_FOR_REGEX = 'REMOTE_COMMAND_FILE'
#assambling a regex list from the ignore on sync list
IGNORE_ON_SYNC_REGEX_LIST = [replace_first_slash(s.replace('REMOTE_COMMAND_FILE', COMMAND_URL_FOR_REGEX).replace('TMP_DIR', TMP_DIR + '/').replace('.', '[.]').replace('*','.*')) for s in IGNORE_ON_SYNC]
SERVER_OWNED_REGEX_LIST = [replace_first_slash(s.replace('.', '[.]').replace('*','.*')) for s in SERVER_OWNED]


try:
    DEPLOY_TOOLS_SYSTEM_FILES_REGEX_LIST = [NORM_COMMAND_FILE.replace('.','[.]'), NORM_TMP_DIR + '/.*', 'wp-config-local\.php$', '^.htaccess$']
except:
    DEPLOY_TOOLS_SYSTEM_FILES_REGEX_LIST = [NORM_TMP_DIR + '/.*', 'wp-config-local\.php$', '^.htaccess$']


