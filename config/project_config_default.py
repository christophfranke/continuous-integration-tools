from constants import * #configuration constants, for more verbose values
#copy this file to ../../project_config.py, so the the project_config.py symlink points to it
#it then gets automatically imported
#this way you can put this file under version control (and change it based on branching)

#The Local DB Name MUST be filled in, if you want to use any database function
LOCAL_DB_NAME = None

#Remote DB Name, User and Password MUST be used, if you want to do any database function
REMOTE_DB_NAME = None
REMOTE_DB_USER = None
REMOTE_DB_PASSWORD = None
REMOTE_DB_HOST = 'localhost' #this is almost always localhost
#REMOTE_DB_PORT = '3306' #optional parameter, usually standard port 3306 is used automatically by server and client
#REMOTE_DB_SOCKET = '' #also optional, because sometimes the mysql client is misconfiguered and then cannot find the socket file by itsself

#the ftp user for ftp uploads
FTP_USER = None
#the ftp pasword for ftp uploads
FTP_PASSWORD = None
#the ftp host to connect to. Often this is the same as the websites domain
FTP_HOST = '' #empty string defaults to LIVE_DOMAIN
#the path to the www dir as seen by the ftp client
FTP_PATH_TO_WWW_DIR = None #we could provide the current path as standard here, but this could lead to chaotic behaviour, if this setting is wrong.
FTP_PROTOCOL = 'ftp' #you may alternatively specify sftp here, though this is untested as for now
FTP_CLIENT = 'ftp' #the command line client that is being used for the ftp connection. Usually there are no problems just using ftp, but in some cases it might be necessary to use sftp.

#note that SSH is currently unavailable, as it is not implemented with the new system yet.
#if an ssh account is provided, this should be preferred (it's faster and more secure)
SSH_USER = None
SSH_PASSWORD = None
SSH_HOST = None #this is usually NOT the same as the websites domain, so we don't provide a standard value here
SSH_PATH_TO_WWW_DIR = None #the path to the www dir as seen by the ssh client

#number of seconds to cooldown before retrying a command after failing it. Not all commands are retried, but sometimes it is beneficial (for example if your ftp connection is refused by the server to reduce workload).
RETRY_TIMEOUT = 5

#the file transfer system decides, how files are being transfered between the local and remote computer. Use SSH if available
TRANSFER_SYSTEM = '' #automatic detection (empty string) will use SSH if SSH_USER, SSH_PASSWORD and SSH_HOST are provided. Possible values are 'FTP' and 'SSH'
#the command system decides, what api is used to execute shell commands on the remote host
COMMAND_SYSTEM = '' #automatic detection works exactly as with the transfer system. Possible values are 'PHP' and 'SSH'. Will use SSH if credentials are provided.

#the www folder relative to the project root
WWW_DIR = 'www' #use '.', if the project root is your www folder. Note, that this is not recommended, this is why we propose a www subfolder as a standard config.

#tmp dir on the remote host, relative to ftp www dir
TMP_DIR = 'deploy-tools-tmp-dir' #note that we already have a local tmp dir in a subdirectory fo the script folder, so we only need a name for a tmp dir on the server that does not collide with anyhting

#If not set the current branch is used.
GIT_BRANCH = '' #optional, but it's good practice to set this to the correct branch to avoid chaos.

#database folder, relative to the project root
DB_DIR = 'Datenbank'

#Do we have a Wordpress install here?
IS_WORDPRESS = True

#the wordpress root folder relative to the www dir. Only needed if IS_WORDPRESS is set to True. You only need to touch this if your wordpress installation is in a subfolder.
WP_DIR = '.'

#This is also important for setting up the local production environment. Overwrites LOCAL_HTTP_ROOT
LOCAL_DOMAIN = None

#This is the live domain of your production server
LIVE_DOMAIN = None

#This var is deprecated. Don't use it in new projects. For backward compatibility we will keep it, but warn if present.
#LOCAL_HTTP_ROOT = None #it is not possible to provide a meaningful default here

#This is the relative directory of the git project root. Do not use starting or trailing slash here.
RELATIVE_LOCAL_PROJECT_ROOT = '..' #the default config is valid, if your script folder is a direct subfolder of your project root

#If you want to turn on the integrated build system for less and js, set this option to True.
ENABLE_BUILD_SYSTEM = False

#If you use the build system, make sure to provide a relataive path form your www-dir to your src-dir and build-dir. Note that they are needed in url form for sourcemaps to work properly.
SRC_URL = None
BUILD_URL = None

#by default your command system is not ready. This is automatically set to true in your project config, if the command system has set up everything and is ready.
#That way it doesn't have to be checked again and again, also you trigger the command system setup by simply removing the line from your project config.
COMMAND_SYSTEM_READY = False

#The Log level. The higher it is set, the more output you will get
LOG_LEVEL = LEVEL_INFO

#If this is not set to None, the complete debug output will be written to this file, in case something went wrong..
OUTPUT_LOG_FILE = 'output/output.log' #relative to script dir

#if your page is protected by basic auth (i.e. .htpasswd protection), you need to provide that information here
NEED_BASIC_AUTH = False #turn on basic auth here
AUTH_USER = None #put your auth username here
AUTH_PASSWORD = None #and your auth password here

#this file holds all the md5 hashes of the all the deployed files, so next time we only upload the files that are really necessary.
DEPLOYED_MD5_TABLE_FILE = 'deployed_files.json' #relative to local root directory
#if we do not always recalculate this table, we use the saved md5 values in our table file DEPLOYED_MD5_TABLE_FILE. However, it seems to be save to always recalculate.
ALWAYS_RECALCULATE_MD5_TABLE = True #the only reason you want to set this to false is if there is no python on the remote, or you are working on a server alone, want to save some time and know what you're doing.

#compression method: possible values are DEFLATE, GZIP, PRECOMPRESSION, NONE
COMPRESSION = 'DEFLATE'

#browser-caching for remote server. The local server always uses no caching. Allowed values are PRODUCTION, DEVELOPMENT, NONE
CACHING = 'DEVELOPMENT'

#these files will be ignored in all sync operations. PHP_COMMAND_FILE and TMP_DIR expand to their corresponding value, * expands to anything (including the empty string)
#Note that the files are evaluated relative to the www folder.
IGNORE_ON_SYNC = ['REMOTE_COMMAND_FILE', 'TMP_DIR', 'wp-config-local.php', '.DS_Store', '.gitignore', 'wp-content/cache/']
