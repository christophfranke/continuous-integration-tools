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
FTP_HOST = '' #defaults to LIVE_DOMAIN

#note that SSH is currently unavailable, as it is not implemented with the new system yet.
#if an ssh account is provided, this should be preferred (it's faster and more secure)
SSH_USER = None
SSH_PASSWORD = None
SSH_HOST = None #this is usually NOT the same as the websites domain, so we don't provide a standard value here

#the file transfer system decides, how files are being transfered between the local and remote computer. Use SSH if available
TRANSFER_SYSTEM = '' #automatic detection (empty string) will use ssh if SSH_USER, SSH_PASSWORD and SSH_HOST are provided. Possible values are 'FTP' and 'SSH'
#the command system decides, what api is used to execute shell commands on the remote host
COMMAND_SYSTEM = '' #automatic detection works exactly as with the transfer system. Possible values are 'PHP' and 'SSH'

#All file actions (deploy, sync_media, etc.) RELY on the projects root folder to be set correctly.
REMOTE_ROOT_DIR = None #this is your remote root directory. If you don't have access to this directory, set it to None. It then is assumed, that the www dir is the root dir on the remote side.
WWW_DIR = 'www' #the www folder relative to the project root. Must be a direct subfolder of the project root.

#tmp dir on the remote host, relative to remote root dir
TMP_DIR = 'deploy-tools-tmp-dir' #note that we already have a local tmp dir in a subdirectory fo the script folder, so we only need a name for a tmp dir on the server that does not collide with anyhting

#If not set the current branch is used.
GIT_BRANCH = '' #optional, but it's good practice to set this to the correct branch to avoid chaos.

#database folder, relative to the project root
DB_DIR = 'Datenbank'

#Do we have a Wordpress install here?
IS_WORDPRESS = True

#the wordpress root folder relative to the project root. Only needed if IS_WORDPRESS is set to True. If WP_DIR is empty, it will be set to whatever value WWW_DIR has.
WP_DIR = ''

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
OUTPUT_LOG_FILE = 'output/output.log'

#if your page is protected by basic auth (i.e. .htpasswd protection), you need to provide that information here
NEED_BASIC_AUTH = False #turn on basic auth here
AUTH_USER = None #put your auth username here
AUTH_PASSWORD = None #and your auth password here

#here you can put project related custom commands that will be executed after deploying.
#this function will be executed within the with cd(REMOTE_WWW_DIR)-block, so that is the folder your in.
def custom_after_deploy_script():
	pass

#will be executed after syncing in the local www-folder with cd(LOCAL_WWW_DIR)
def custom_after_sync_script():
	pass