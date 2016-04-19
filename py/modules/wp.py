import out
import engine
import run
import os


@out.indent
def overwrite_allowed(file, when_exists = 'quit'):
    if os.path.isfile(file):
        if when_exists == 'quit':
            out.log(file + ' already exists.', 'wordpress', out.LEVEL_ERROR)
            engine.quit()
        if when_exists == 'skip':
            out.log(file + ' already exists. skipped.', 'wordpress')
            return False
        if when_exists == 'overwrite':
            out.log(file + ' already exists. overwriting.', 'wordpress')
            return True
    else:
        return True


@out.indent
def copy_wp_config(when_exists = 'skip'):
    out.log('copy wp-config.php to wordpress directory', 'wordpress')
    
    #check if wp-config.php already exists
    if overwrite_allowed(engine.LOCAL_WP_DIR + '/wp-config.php', when_exists):
        #copy our config.php to the desired location
        run.local('cp php/wordpress/wp-config.php ' + engine.LOCAL_WP_DIR)

@out.indent
def create_wp_config_local(when_exists = 'overwrite'):
    out.log('create wp-config-local.php in wordpress directory...', 'wordpress')
    if overwrite_allowed(engine.LOCAL_WP_DIR + '/wp-config-local.php', when_exists):
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
        file.write("define('WP_DEBUG', True);\n")
        file.write("define('WP_DEBUG_DISPLAY', True);\n")
        #done, close
        file.close()

@out.indent
def create_wp_salt(when_exists = 'skip'):
    out.log('creating wp-salt.php in wordpress directory...', 'wordpress')
    if overwrite_allowed(engine.LOCAL_WP_DIR + '/wp-salt.php', when_exists):
        run.local('echo "<?php">' + engine.LOCAL_WP_DIR + '/wp-salt.php')
        run.local('curl --silent ' + engine.WORDPRESS_SALT_URL + ' >>' + engine.LOCAL_WP_DIR + '/wp-salt.php')

@out.indent
def create_wp_config_live(when_exists = 'overwrite'):
    out.log('create wp-config-live.php in wordpress directory...', 'wordpress')
    filename = engine.LOCAL_WP_DIR + '/wp-config-live.php'
    if overwrite_allowed(filename, when_exists):
        #open file
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
