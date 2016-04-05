import out
import engine
import run
import os


@out.indent
def copy_wp_config():
    out.log('copy wp-config.php to wordpress directory', 'wordpress')
    #check if wp-config.php already exists
    if os.path.isfile(engine.LOCAL_WWW_DIR + '/wp-config.php'):
        out.log("wp-config.php already exists at " + engine.LOCAL_WP_DIR + '. You have to delete this file in order to proceed with this command. If you are not sure about potentially important information in your current wp-config.php, make a backup before deleting it.', 'wordpress', out.LEVEL_ERROR)
        engine.quit()

    #copy our config.php to the desired location
    run.local('cp php/wordpress/wp-config.php ' + engine.LOCAL_WP_DIR)

@out.indent
def create_wp_config_local():
    out.log('create wp-config-local.php in wordpress directory', 'wordpress')
    #open file
    file = open(engine.LOCAL_WP_DIR + '/wp-config-local.php', 'w')
    #delete content
    file.truncate()
    #write new content
    file.write("<?php\n")
    file.write("define('DB_NAME', '" + engine.LOCAL_DB_NAME + "');\n")
    file.write("define('DB_USER', '" + engine.LOCAL_DB_USER + "');\n")
    file.write("define('DB_PASSWORD', '" + engine.LOCAL_DB_PASSWORD + "');\n")
    file.write("define('DB_HOST', '" + engine.LOCAL_DB_HOST + "');\n")
    file.write("define('WP_SITEURL', '" + engine.LOCAL_ROOT_URL + "');\n")
    #done, close
    file.close()

@out.indent
def create_wp_salt():
    out.log('creating wp-salt.php in wordpress directory', 'wordpress')
    run.local('echo "<?php">' + engine.LOCAL_WP_DIR + '/wp-salt.php')
    run.local('curl --silent ' + engine.WORDPRESS_SALT_URL + ' >>' + engine.LOCAL_WP_DIR + '/wp-salt.php')

@out.indent
def create_wp_config_live():
    #open file
    filename = engine.LOCAL_WP_DIR + '/wp-config-live.php'
    file = open(filename, 'w')
    #delete current content
    file.truncate()
    #write new content
    file.write("<?php\n")
    file.write("define('DB_NAME', '" + engine.REMOTE_DB_NAME + "');\n")
    file.write("define('DB_USER', '" + engine.REMOTE_DB_USER + "');\n")
    file.write("define('DB_PASSWORD', '" + engine.REMOTE_DB_PASSWORD + "');\n")
    file.write("define('DB_HOST', '" + engine.REMOTE_DB_HOST + "');\n")
    file.write("define('WP_SITEURL', '" + engine.REMOTE_ROOT_URL + "');\n")
    #done, close
    file.close()
