from fabric.api import env
#copy this file to ../project_config.py, so the the project_config.py symlink points to it
#it then gets automatically imported by fab
#this way you can put this file under version control (and change it based on branching)

#The Local DB Name MUST be filled in, if you want to use any database function
LOCAL_DB_NAME = 'local database name'

#these MUST be filled in, otherwise the whole process does not work. If there is no SSH-connection available, use the ragusescheer.de preview server
env.hosts = ['ssh server name']
env.user = 'ssh user name'
env.password = 'ssh password'

#Remote DB Name, User and Password MUST be used, if you want to do any database function
REMOTE_DB_NAME = 'remote database name'
REMOTE_DB_USER = 'remote database user'
REMOTE_DB_PASSWORD = 'remote database password'
REMOTE_DB_HOST = 'localhost' #this is almost always localhost
#REMOTE_DB_PORT = '3306' #optional parameter, usually standard port 3306 is used automatically by server and client
#REMOTE_DB_SOCKET = '' #also optional, because sometimes the mysql client is misconfiguered and then cannot find the socket file by itsself

#All file actions (deploy, sync_media, etc.) RELY on the projects root folder to be set correctly.
REMOTE_ROOT_FOLDER = 'remote root folder' #this is your remote root folder (must be the git project root). Should be an absolute path, but relative paths usually also work.
WWW_FOLDER = 'www' #the www folder relative to the project root

#If not set the current branch is used.
GIT_BRANCH = 'master' #optional, but it's good practice to set this to the correct branch to avoid chaos.

#the project root folder relative to the script folder. Optional, defaults to '..', which is the usual case when we have the script folder in a direct subfolder of the project root
#RELATIVE_LOCAL_PROJECT_ROOT = '..'

#database folder, defaults to 'Datenbank'
DB_FOLDER = 'Datenbank'

#Do we have a Wordpress install here?
IS_WORDPRESS = True

#the wordpress root folder relative to the project root. Only needed if IS_WORDPRESS is set to True. If WP_FOLDER is set to None, it will be set to the final value of WWW_FOLDER.
WP_FOLDER = None

#For the crawler, so it can crawl this domain. Use http:// without trailing slash, example: http://ragusescheer.local
LCOAL_HTTP_ROOT = None #it is not possible to provide a meaningful default here

#This is the relative directory of the git project root. Do not use starting or trailing slash here.
RELATIVE_LOCAL_PROJECT_ROOT = '..' #the default config is valid, if your script folder is a direct subfolder of your project root


#here you can put project related custom commands that will be executed after deploying.
#this function will be executed within the with cd(REMOTE_WWW_FOLDER)-block, so that is the folder your in.
def custom_after_deploy_script():
	pass

#will be executed after syncing in the local www-folder with cd(LOCAL_WWW_FOLDER)
def custom_after_sync_script():
	pass