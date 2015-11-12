#copy this file to config.py and fill in your custom system configuration
from fabric.api import env
import os

env.hosts = ['ssh server name']
env.user = 'ssh user name'
env.password = 'ssh password'

REMOTE_DB_NAME = 'remote database name'
REMOTE_DB_USER = 'remote database user'
REMOTE_DB_PASSWORD = 'remote database password'
REMOTE_DB_HOST = 'localhost' #this is almost always localhost

LOCAL_DB_NAME = 'local database name'
LOCAL_DB_USER = 'root' #these are usual our settings
LOCAL_DB_PASSWORD = '51515151' #and these
LOCAL_DB_HOST = '127.0.0.1' #and these. note that there might be problems with 'localhost' instead of 127.0.0.1

LOCAL_HTTP_NAME = LOCAL_DB_NAME #this is the name of the symlink, that the script will create for you. defaults to you database name

REMOTE_ROOT_FOLDER = 'tondeo-test-www' #this is your remote www folder (might be a subfolder of the project root)
LOCAL_ROOT_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/..' #this is the local www folder. you can leave this setting, if you place the script in a direct subfolder of your www folder.

#here you can put project related custom commands that will be executed after deploying.
#this function will be executed within the with(REMOTE_ROOT_FOLDER)-block, so that is the folder your in.
def custom_after_deploy_script():
	pass