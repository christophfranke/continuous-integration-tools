#copy this file to config.py and fill in your custom system configuration
from fabric.api import env
import os

LOCAL_DB_USER = 'root' #these are usual our settings
LOCAL_DB_PASSWORD = '51515151' #and these
LOCAL_DB_HOST = '127.0.0.1' #and these. note that there might be problems with 'localhost' instead of 127.0.0.1

LOCAL_APACHE_ERROR_LOG = '/var/log/apache2/error_log' #here you usually find your apache error log on mac osx
LOCAL_ETC_HOSTS = '/etc/hosts'
LOCAL_HTTPD_CONF = '/etc/apache2/httpd.conf'


#This URL creates a random salt for us
WORDPRESS_SALT_URL = 'https://api.wordpress.org/secret-key/1.1/salt/'