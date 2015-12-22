from fabric.api import env
#copy this file to ../project_config.py, so the the project_config.py symlink points to it
#it then gets automatically imported by fab
#this way you can put this file under version control (and change it based on branching)

LOCAL_DB_NAME = 'local database name'

env.hosts = ['ssh server name'] #host name for ssh login
env.user = 'ssh user name'
env.password = 'ssh password'

REMOTE_DB_NAME = 'remote database name'
REMOTE_DB_USER = 'remote database user'
REMOTE_DB_PASSWORD = 'remote database password'
REMOTE_DB_HOST = 'localhost' #this is almost always localhost

REMOTE_ROOT_FOLDER = 'remote root folder' #this is your remote root folder (must be the project root). Should be an absolute path
WWW_FOLDER = 'www' #the www folder relative to the project root
#WP_FOLDER = 'www/blog' #the wordpress root folder relative to the project root, must not be set, defaults to WWW_FOLDER

GIT_BRANCH = 'master'

#here you can put project related custom commands that will be executed after deploying.
#this function will be executed within the with cd(REMOTE_ROOT_FOLDER)-block, so that is the folder your in.
def custom_after_deploy_script():
	pass

