import out
import engine
import run
import os




@out.indent
def pack_remote(files):
    out.log('packing on remote: ' + files, 'tar')
    if not validate_files(files):
        out.log('files need to be given relative to root dir.', 'tar', out.LEVEL_ERROR)
        engine.quit()
    tar_file = engine.get_new_remote_file('tar')
    run.remote('tar cf ' + tar_file + ' -C ' + engine.REMOTE_ROOT_DIR + ' ' + files)

    return tar_file

@out.indent
def pack_local(files):
    out.log('packing locally: ' + files, 'tar')
    if not validate_files(files):
        out.log('files need to be given relative to root dir.', 'tar', out.LEVEL_ERROR)
        engine.quit()
    tar_file = engine.get_new_local_file('tar')
    run.local('tar cf ' + tar_file + ' -C ' + engine.LOCAL_ROOT_DIR + ' ' + files)

    return tar_file

def unpack_local(archive):
    out.log('unpacking locally: ' + archive, 'tar')
    run.local('cd ' + engine.LOCAL_ROOT_DIR + ' && tar xf ' + archive)

def unpack_remote(archive):
    out.log('unpacking on remote: ' + archive, 'tar')
    run.remote('cd ' + engine.REMOTE_ROOT_DIR + ' && tar xf ' + archive)

def validate_files(files):
    files_array = files.split()
    for file in files_array:
        if os.path.isabs(file):
            return False

    #no absolute path detected, we should be save now
    return True