#copy this file to config.py and fill in your custom system configuration

#you might want to put this in you global config file, expected at ~/.deploy-tools/config.py
LOCAL_DB_USER = None
LOCAL_DB_PASSWORD = None #and these
LOCAL_DB_HOST = '127.0.0.1' #note that there might be problems with 'localhost' instead of 127.0.0.1

#standard config for osx
LOCAL_APACHE_ERROR_LOG = '/var/log/apache2/error_log' #here you usually find your apache error log on mac osx
LOCAL_ETC_HOSTS = '/etc/hosts' #hosts config file for looking up ip addresses
LOCAL_HTTPD_CONF = '/etc/apache2/httpd.conf' #apache config file

#This URL creates a random salt for us
WORDPRESS_SALT_URL = 'https://api.wordpress.org/secret-key/1.1/salt/'
