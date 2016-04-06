from modules import engine
from modules import out
from modules import wp

@engine.prepare_and_clean
def execute(overwrite = None):
    out.log("Creating wordpress config files from local config settings...")
    #copy wp-config.php
    if overwrite == 'overwrite':
        wp.copy_wp_config(True)
    else:
        wp.copy_wp_config(False)
    #creaet wp-salt.php
    wp.create_wp_salt()
    #create wp-config-local.php
    wp.create_wp_config_local()
    #create wp-config-live.php
    wp.create_wp_config_live()
    #done


def help():
    out.log("This command creates 4 files for you:", 'help')
    out.log("wp-config.php contains the standard settings without database credentials or salt, but with a command to import these settings from the corresponding other files.", 'help')
    out.log("wp-config-local.php holds the credentials for the local database. Will be included by wp-config.php if it exists. Is being ignored by sync by default, i.e. it doesn't get uploaded to your server.", 'help')
    out.log('wp.config-live.php holds the credentials of the live database. wp-config.php will require this file if there is no wp-config-local.php present, such as in the live server environment.', 'help')
    out.log('wp-salt.php holds the salt defines needed by wordpress. The defines are being acquired online by the wordpress api. This file is required by wp-config.php. Note that this changes all the salts used by wordpress, which will result in logging out all currently logged in users.', 'help')
    out.log('note that this command only works if there is no wp-config.php present already, in order to prevent you from losing relevant data.', 'help')