import out
import engine
import run
import os


@out.indent
def overwrite_allowed(filename, when_exists = 'quit'):
    import file
    if file.local_not_empty(filename):
        if when_exists == 'quit':
            out.log(filename + ' already exists.', 'wordpress', out.LEVEL_ERROR)
            engine.quit()
        if when_exists == 'skip':
            out.log(filename + ' already exists. skipped.', 'wordpress')
            return False
        if when_exists == 'overwrite':
            out.log(filename + ' already exists. overwriting.', 'wordpress')
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
    import file
    out.log('create wp-config-local.php in wordpress directory...', 'wordpress')
    if overwrite_allowed(engine.LOCAL_WP_DIR + '/wp-config-local.php', when_exists):
        #assemble filenmae
        filename = engine.LOCAL_WP_DIR + '/wp-config-local.php', 'w'

        #assemble content
        content = "<?php\n"
        content = content + "define('DB_NAME', '" + engine.LOCAL_DB_NAME + "');\n"
        content = content + "define('DB_USER', '" + engine.LOCAL_DB_USER + "');\n"
        content = content + "define('DB_PASSWORD', '" + engine.LOCAL_DB_PASSWORD + "');\n"
        content = content + "define('DB_HOST', '" + engine.LOCAL_DB_HOST + "');\n"
        content = content + "define('WP_SITEURL', '" + engine.LOCAL_ROOT_URL + "');\n"
        content = content + "define('WP_DEBUG', True);\n"
        content = content + "define('WP_DEBUG_DISPLAY', True);\n"
        content = content + "define('WP_CACHE', False);\n"

        #write file
        file.write_local(content, filename = filename)

@out.indent
def create_wp_salt(when_exists = 'skip'):
    out.log('creating wp-salt.php in wordpress directory...', 'wordpress')
    if overwrite_allowed(engine.LOCAL_WP_DIR + '/wp-salt.php', when_exists):
        run.local('echo "<?php">' + engine.LOCAL_WP_DIR + '/wp-salt.php')
        run.local('curl --silent ' + engine.WORDPRESS_SALT_URL + ' >>' + engine.LOCAL_WP_DIR + '/wp-salt.php')

@out.indent
def create_wp_config_live(when_exists = 'overwrite'):
    import file
    out.log('create wp-config-live.php in wordpress directory...', 'wordpress')
    filename = engine.LOCAL_WP_DIR + '/wp-config-live.php'
    if overwrite_allowed(filename, when_exists):

        #assemble new content
        content = "<?php\n"
        content = content + "define('DB_NAME', '" + engine.REMOTE_DB_NAME + "');\n"
        content = content + "define('DB_USER', '" + engine.REMOTE_DB_USER + "');\n"
        content = content + "define('DB_PASSWORD', '" + engine.REMOTE_DB_PASSWORD + "');\n"
        content = content + "define('DB_HOST', '" + engine.REMOTE_DB_HOST + "');\n"
        content = content + "define('WP_SITEURL', '" + engine.REMOTE_ROOT_URL + "');\n"

        #done, write
        file.write_local(content, filename = filename)
