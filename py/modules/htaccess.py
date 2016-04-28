import engine
import out
import run
import transfer

import os



@out.indent
def create_local_symlink():
    out.log('creating local .htaccess link', 'htaccess')
    run.local('cd ' + engine.LOCAL_WWW_DIR + ' && ln -s .htaccess.local .htaccess')

@out.indent
def create_remote_symlink():
    out.log('creating remote .htaccess link', 'htaccess')
    run.remote('ln -s .htaccess.live .htaccess')

def prepare(overwrite, upload=False):
    htaccess_file = os.path.abspath(engine.LOCAL_WWW_DIR + '/.htaccess')
    if os.path.isfile(htaccess_file):
        if overwrite == 'fail':
            out.log('.htaccess already exists. Specify overwrite as parameter or delete the file manually before trying again.', 'htaccess', out.LEVEL_ERROR)
            engine.quit()
        if overwrite == 'overwrite':
            run.local('rm ' + htaccess_file)
    if upload:
        transfer.remove_remote('.htaccess')

def assemble_htaccess_data(domain):
    ht_data = engine.read_local_file(engine.SCRIPT_DIR + '/htaccess/signature.htaccess')
    ht_data += engine.read_local_file(engine.SCRIPT_DIR + '/htaccess/common.htaccess')
    ht_data += engine.read_local_file(engine.SCRIPT_DIR + '/htaccess/deflate.htaccess')
    #caching only for live site
    if domain == 'live':
        ht_data += engine.read_local_file(engine.SCRIPT_DIR + '/htaccess/caching.htaccess')
    else:
        #explicitly disable browsercaching for all assets for local development site
        ht_data += engine.read_local_file(engine.SCRIPT_DIR + '/htaccess/no-caching.htaccess')
    if os.path.isfile(engine.LOCAL_WWW_DIR + '/.htaccess.custom'):
        ht_data += engine.read_local_file(engine.LOCAL_WWW_DIR + '/.htaccess.custom')
    if engine.IS_WORDPRESS:
        ht_data += engine.read_local_file(engine.SCRIPT_DIR + '/htaccess/wordpress.htaccess')

    if domain == 'live':
        if engine.NEED_BASIC_AUTH:
            ht_data += engine.read_local_file(engine.SCRIPT_DIR + '/htaccess/basic-auth.htaccess')

    return ht_data

@out.indent
def create_local_file():
    out.log('creating .htaccess.local', 'htacecss')

    ht_data = assemble_htaccess_data('local')
    engine.write_local_file(ht_data, filename = engine.LOCAL_WWW_DIR + '/.htaccess.local')

@out.indent
def create_live_file(upload=False):
    out.log('creating .htaccess.live', 'htaccess')
    ht_data = assemble_htaccess_data('live')
    if engine.NEED_BASIC_AUTH:
        #get absolute path to remote passwd and inject it into ht_data
        remote_passwd_file = engine.get_remote_www_dir_abspath() + '/.htpasswd'
        ht_data = ht_data.replace('[HTPASSWD_FILE]', remote_passwd_file)
        #create passwd file
        run.local('htpasswd -bc ' + engine.LOCAL_WWW_DIR + '/.htpasswd ' + engine.AUTH_USER + ' ' + engine.AUTH_PASSWORD, halt_on_stderr = False)
        transfer.put(engine.LOCAL_WWW_DIR + '/.htpasswd', '.htpasswd')

    #write local
    engine.write_local_file(ht_data, filename = engine.LOCAL_WWW_DIR + '/.htaccess.live')
    #write to remote
    if upload:
        engine.write_remote_file(ht_data, filename = '.htaccess.live')
