from getpass import getpass
from fabric.api import local
from project_config_example import *
from datetime import datetime
import re


#get input variable
def get_input(const_name, help_text = ''):
    #get default
    try:
        #try current project config first
        default = current_conf_dict[const_name]
    except KeyError:
        try:
            #try project config example next
            exec('default = ' + const_name)
        except NameError:
            default = None

    #set default text
    if default is not None:
        default_text = '[' + default + ']'
    else:
        default_text = '[None]'

    #read from stdin and set value
    value = raw_input(const_name + ' ' + help_text + ' ' + default_text + ': ')
    if value != '':
        new_conf_dict[const_name] = value
    else:
        try:
            new_conf_dict[const_name] = current_conf_dict[const_name]
        except KeyError:
            pass

#filter constant names: valid constant names contain of only uppercase letters and underscores
def valid_constant(const_name):
    if re.match('(_|[A-Z])+$', const_name):
        return True
    else:
        return False

#read the current project config file and save the variables in a dictionary
def read_project_config_vars():
    conf_dict = {}
    try:
        import project_config
        constants = filter(valid_constant, dir(project_config))
        for const in constants:
            conf_dict[const] = vars(project_config)[const]
    except ImportError:
        pass

    return conf_dict


#setup dictionaries
new_conf_dict = {}
current_conf_dict = read_project_config_vars()


def run():

    #print some info
    print "You will be asked some setup questions. Those Configs will be written to ../project_config.py"
    print "If you mistyped something or want to change something later on, just open it and change the setting."
    print "If you want to skip a certain setting, just press enter. A standard value will be used then"
    print "You always can run this setup again by typing 'fab setup_project'."

    #ssh vars
    get_input('SSH_HOST', 'is the server to connect via ssh')
    get_input('SSH_USER', 'is the user name to connect with via ssh')
    get_input('SSH_PASSWORD', 'is the ssh password')

    #local db
    get_input('LOCAL_DB_NAME', 'is the name of the local database you want to use. It will be created, if it does not exists')

    #remote db
    get_input('REMOTE_DB_NAME', 'is the name of the remote database. Note that this will not becreated for you')
    get_input('REMOTE_DB_USER', 'is the remote mysql user')
    get_input('REMOTE_DB_PASSWORD', 'is the remote mysql password')
    get_input('REMOTE_DB_HOST', 'is the remote sql server name')

    #remote folders
    get_input('REMOTE_ROOT_FOLDER', 'is the remote root folder. It is recommmended to use an absolute path, though possible to use a relative path')
    get_input('WWW_FOLDER', 'is the project subfolder the webserver points to')

    #http urls
    get_input('LOCAL_DOMAIN', 'is the domain name that will be set up in your local environment. Do NOT use http://')
    get_input('LIVE_DOMAIN', 'is the domain of your production server. Do NOT use http://')

    #write project config file
    filename = '../project_config.py'
    file = open(filename, 'a')
    file.write("#config below was automatically created by project config setup wizard.\n#Timestamp: " + str(datetime.now()) + ".\n\n")
    for const in new_conf_dict:
        command = const + " = '" + new_conf_dict[const] + "'"
        file.write(command + "\n")
    file.write("PROJECT_CONFIG_OK = True\n")
    file.close()
    print "New project_config file has been written. To use the new project config settungs, please run the command again."
    exit()
