#import datetime for timestamp constant
from datetime import datetime

#in case of a constant set in multiple config files, the latest import counts.

#import example configs first
from config_example import *
from project_config_example import *

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FAB_FILE = SCRIPT_DIR + '/fabfile.py'

#then try to import project configs in project folder
try:
    from project_config import *
except ImportError:
    #if there is no project config, run the setup wizard
    import project_config_setup
    project_config_setup.run()

#finally, try to get config.py file in this folder
try:
    from config import *
except ImportError:
    pass


#now we should have the configuration ready to setup all the constants we need
try:
    SSH_HOST
    if not SSH_HOST is None:
        env.hosts = [SSH_HOST]
except NameError:
    pass

try:
    SSH_USER
    if not SSH_USER is None:
        env.user = SSH_USER
except NameError:
    pass
try:
    SSH_PASSWORD
    if not SSH_PASSWORD is None:
        env.password = SSH_PASSWORD
except NameError:
    pass


LOCAL_ROOT_FOLDER = os.path.abspath(SCRIPT_DIR + '/' + RELATIVE_LOCAL_PROJECT_ROOT)
LOCAL_WWW_FOLDER = LOCAL_ROOT_FOLDER + '/' + WWW_FOLDER

LOCAL_DB_FOLDER = LOCAL_ROOT_FOLDER + '/' + DB_FOLDER

SQL_DUMP_FILE = LOCAL_DB_FOLDER + '/dump-' + str(datetime.now()).replace(' ', '-') + '.sql'
SQL_GZ_DUMP_FILE = SQL_DUMP_FILE + '.gz'

try:
    LOCAL_HTTP_ROOT
    print "Warning: LOCAL_HTTP_ROOT is deprecated. Use LOCAL_DOMAIN instead (and omit the http:// there)."
except NameError:
    try:
        LOCAL_HTTP_ROOT = 'http://' + LOCAL_DOMAIN
    except:
        LOCAL_HTTP_ROOT = None
        print "Warning: LOCAL_HTTP_ROOT could not be assembled by script. Try running update_config to have them set automatically or edit your project_config.py."

try:
    REMOTE_HTTP_ROOT = 'http://' + LIVE_DOMAIN
except:
    print "Warning: REMOTE_HTTP_ROOT could not be assembled by script. Try running update_config to have them set automatically or edit your project_config.py."

REMOTE_WWW_FOLDER = REMOTE_ROOT_FOLDER + '/' + WWW_FOLDER
try:
    LOCAL_MYSQL = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '
    LOCAL_MYSQLDUMP = 'mysqldump -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '
    LOCAL_MYSQL_NO_DB = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' '
except:
    print "Warning: LOCAL_MYSQL could not be assembled by script. Try running update_config to have them set automatically or edit your project_config.py."

#concatenate mysql command strings
try:
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
except:
    print "Warning: REMOTE_MYSQL_PARAMS could not be assembled by script. Try running update_config to have them set automatically or edit your project_config.py."


FABRIC_TMP_DIR = 'fabric-tmp-dir'
TMP_SQL_FILE = 'fabric-tmp.sql'
SSH_TMP_FILE = FABRIC_TMP_DIR + '/ssh-key-tmp-file'
UPLOAD_FILE_TO_REMOTE_FILENAME = 'upload-file-to-remote-filename.sql'

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


if IS_WORDPRESS:
    if WP_FOLDER is None:
        WP_FOLDER = WWW_FOLDER
    LOCAL_WP_FOLDER = LOCAL_ROOT_FOLDER + '/' + WP_FOLDER
    REMOTE_WP_FOLDER = REMOTE_ROOT_FOLDER + '/' + WP_FOLDER

try:
    WP_FOLDER
except:
    WP_FOLDER = WWW_FOLDER


try:
    TRUNCATE_LOCAL_DB_SQL = 'DROP DATABASE `' + LOCAL_DB_NAME + '`;CREATE DATABASE `' + LOCAL_DB_NAME + '`;'
except:
    print "Warning: TRUNCATE_LOCAL_DB_SQL could not be assembled by script. Try running update_config to have them set automatically or edit your project_config.py."
try:
    TRUNCATE_REMOTE_DB_SQL = 'DROP DATABASE `' + REMOTE_DB_NAME + '`;CREATE DATABASE `' + REMOTE_DB_NAME + '`;'
except:
    print "Warning: TRUNCATE_REMOTE_DB_SQL could not be assembled by script. Try running update_config to have them set automatically or edit your project_config.py."


