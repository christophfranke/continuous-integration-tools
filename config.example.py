#copy this file to config.py and fill in your custom system configuration
from fabric.api import env
import os

LOCAL_DB_USER = 'root' #these are usual our settings
LOCAL_DB_PASSWORD = '51515151' #and these
LOCAL_DB_HOST = '127.0.0.1' #and these. note that there might be problems with 'localhost' instead of 127.0.0.1

LOCAL_WWW_FOLDER = '..' #this is the relative path to the local www folder.

