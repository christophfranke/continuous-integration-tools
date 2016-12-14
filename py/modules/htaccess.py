import engine
import out
import run




@out.indent
def create_local_symlink():
    out.log('creating local .htaccess link', 'htaccess')
    run.local('cd ' + engine.LOCAL_WWW_DIR + ' && ln -s .htaccess.local .htaccess')

@out.indent
def create_remote_symlink():
    out.log('creating remote .htaccess link', 'htaccess')
    run.remote('ln -s .htaccess.live .htaccess')

def prepare(overwrite, upload=False):
    import os
    import file

    htaccess_file = os.path.abspath(engine.LOCAL_WWW_DIR + '/.htaccess')
    if file.local_not_empty(htaccess_file):
        if overwrite == 'fail':
            out.log('.htaccess already exists. Specify overwrite as parameter or delete the file manually before trying again.', 'htaccess', out.LEVEL_ERROR)
            engine.quit()
        if overwrite == 'overwrite':
            run.local('rm ' + htaccess_file)
    if upload:
        import transfer
        transfer.remove_remote('.htaccess')

def assemble_htaccess_data(domain):
    import file

    ht_data = file.read_local(engine.SCRIPT_DIR + '/htaccess/signature.htaccess')
    ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/common.htaccess')
    if engine.COMPRESSION == 'DEFLATE':
        ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/deflate.htaccess')
    elif engine.COMPRESSION == 'GZIP':
        ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/gzip.htaccess')
    elif engine.COMPRESSION == 'PRECOMPRESSION':
        ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/precompression.htaccess')
    elif engine.COMPRESSION == None or engine.COMPRESSION == False or engine.COMPRESSION == 'NONE':
        pass
    else:
        out.log('Error: Invalid value for COMPRESSION: ' + str(engine.COMPRESSION) + '. Use DEFLATE, GZIP, PRECOMPRESSION or NONE instead.', 'htaccess', out.LEVEL_ERROR)
    #caching only for live site
    if domain == 'live':
        if engine.CACHING == 'DEVELOPMENT':
            ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/caching-development.htaccess')
        elif engine.CACHING == 'PRODUCTION':
            ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/caching-production.htaccess')
        elif engine.CACHING == None or engine.CACHING == False or engine.CACHING == 'NONE':
            ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/caching-none.htaccess')
        else:
            out.log('Warning: You have not specified a valid browser caching strategy: ' + str(engine.CACHING) + '. Use PRODUCTION, DEVELOPMENT or NONE instead.', 'htaccess', out.LEVEL_WARNING)
    else:
        #explicitly disable browsercaching for all assets for local development site
        ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/caching-none.htaccess')
    if file.local_not_empty(engine.LOCAL_WWW_DIR + '/.htaccess.custom'):
        ht_data += file.read_local(engine.LOCAL_WWW_DIR + '/.htaccess.custom')
    if engine.IS_WORDPRESS:
        ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/wordpress.htaccess')

    if domain == 'live':
        if engine.NEED_BASIC_AUTH:
            ht_data += file.read_local(engine.SCRIPT_DIR + '/htaccess/basic-auth.htaccess')

    return ht_data

@out.indent
def create_local_file():
    import file
    out.log('creating .htaccess.local', 'htacecss')

    ht_data = assemble_htaccess_data('local')
    file.write_local(ht_data, filename = engine.LOCAL_WWW_DIR + '/.htaccess.local')

@out.indent
def create_live_file(upload=False):
    import file

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
    file.write_local(ht_data, filename = engine.LOCAL_WWW_DIR + '/.htaccess.live')
    #write to remote
    if upload:
        file.write_remote(ht_data, filename = '.htaccess.live')
