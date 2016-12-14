import out

#remember the files we have created for cleaning up later
current_tmp_file_namespace = 'global'
local_tmp_files = {}
local_tmp_files['global'] = []
remote_tmp_files = {}
remote_tmp_files['global'] = []
remote_tmp_dir_created = False

#decorator for cleaning up immediately
#this function is deprecated, because it almost never makes sense to mix this up
def cleanup_tmp_files(func):
    def cleanup_immediately_func(*args, **kwargs):
        #change but remember namespace
        global current_tmp_file_namespace
        old_tmp_file_namespace = current_tmp_file_namespace
        current_tmp_file_namespace = get_random_id()
        local_tmp_files[current_tmp_file_namespace] = []
        remote_tmp_files[current_tmp_file_namespace] = []
        result = func(*args, **kwargs)
        cleanup(current_tmp_file_namespace)
        current_tmp_file_namespace = old_tmp_file_namespace
        return result
    return cleanup_immediately_func

def remove_tmp_dir():
    import engine
    global remote_tmp_dir_created
    if remote_tmp_dir_created:
        import transfer
        transfer.remove_remote_directory(engine.NORM_TMP_DIR)
        remote_tmp_dir_created = False

#cleanup is being run at the very end. cleans up all the files that have been created in the process.
@out.indent
def cleanup(namespace = None, local = True, remote = True):
    #cleanup all namespaces
    if namespace is None:

        #make a copy of the list before iterating over it
        up_for_delete_list = list(local_tmp_files)
        #cleanup every entry of this list
        for name in up_for_delete_list:
            cleanup(name, local, remote)

        #remove guard and exit
        cleaning_up_already = False
        return

    import transfer
    out.log('Removing tmp files in namespace ' + namespace, 'cleanup', out.LEVEL_DEBUG)
    #remove remote files first, because there removal might cause local files to happen
    if remote:
        for file in remote_tmp_files[namespace]:
            transfer.remove_remote(file)
            remote_tmp_files[namespace] = []

    #then remove local files
    if local:
        for file in local_tmp_files[namespace]:
            transfer.remove_local(file)
            local_tmp_files[namespace] = []


@out.indent
def cleanup_local():
    out.log('cleaning up local tmp files...', 'engine', out.LEVEL_VERBOSE)
    cleanup(remote = False)

@out.indent
def cleanup_remote():
    out.log('cleaning up remote tmp files...', 'engine', out.LEVEL_VERBOSE)
    cleanup(local = False)

#returns the name of the local tmp dir. It exists, because it has a .gitignore in it.
def get_local_tmp_dir():
    import engine
    return engine.LOCAL_TMP_DIR

#returns the name of the remote tmp dir and ensures it exists.
def get_remote_tmp_dir():
    import transfer
    import engine
    global remote_tmp_dir_created
    if not remote_tmp_dir_created:
        transfer.create_remote_directory(engine.NORM_TMP_DIR, 777)
        remote_tmp_dir_created = True
    return engine.NORM_TMP_DIR

def clean_local_tmp_dir():
    import file
    import run
    #create a file, so the removal does not fail
    tmp_file = file.write_local('this file is here to be cleaned up.')
    #unregister it, because it gets wiped by this cleanup already
    unregister_local_file(tmp_file)
    local_tmp_dir = get_local_tmp_dir()
    run.local('rm ' + local_tmp_dir + '/tmp_file_*')

def clean_remote_tmp_dir():
    #import transfer
    import run
    remote_tmp_dir = get_remote_tmp_dir()
    run.remote('rm -f ' + remote_tmp_dir + '/*')

@out.indent
def register_local_file(filename):
    out.log('Registered local tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global local_tmp_files
    global current_tmp_file_namespace
    local_tmp_files[current_tmp_file_namespace].append(filename)

@out.indent
def register_remote_file(filename):
    out.log('Registered remote tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global remote_tmp_files
    global current_tmp_file_namespace
    remote_tmp_files[current_tmp_file_namespace].append(filename)

@out.indent
def unregister_local_file(filename):
    out.log('Unregister local tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global local_tmp_files
    global current_tmp_file_namespace
    local_tmp_files[current_tmp_file_namespace].remove(filename)

@out.indent
def unregister_remote_file(filename):
    out.log('Registered remote tmp file ' + filename, 'engine', out.LEVEL_DEBUG)
    global remote_tmp_files
    global current_tmp_file_namespace
    remote_tmp_files[current_tmp_file_namespace].remove(filename)


@out.indent
def rename_file(from_file, to_file, file_list):
    out.log('Registered file for renaming ' + from_file + ' -> ' + to_file, 'engine', out.LEVEL_DEBUG)
    global current_tmp_file_namespace
    #define filter function
    def filter(filename):
        if filename == from_file:
            return to_file
        else:
            return filename
    #filter list with that functino
    file_list[current_tmp_file_namespace] = [filter(filename) for filename in file_list[current_tmp_file_namespace]]

def rename_local_file(from_file, to_file):
    return rename_file(from_file, to_file, local_tmp_files)

def rename_remote_file(from_file, to_file):
    return rename_file(from_file, to_file, remote_tmp_files)
