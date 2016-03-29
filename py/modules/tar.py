import out
import engine
import run
import os




@out.indent
def pack_remote(files):
    #tell
    out.log('packing on remote: ' + files, 'tar')

    #validate files
    if not validate_files(files):
        out.log('Error: files need to be given relative to www dir.', 'tar', out.LEVEL_ERROR)
        engine.quit()

    #register tar file
    tar_file = engine.get_new_remote_file('tar')

    #assemble packing command. Always pack from www dir
    pack_command = 'tar cf ' + tar_file + ' --exclude .tar --exclude ' + engine.TMP_DIR + ' -C ' + engine.REMOTE_WWW_DIR + ' ' + files

    #pack!
    run.remote(pack_command)

    #and return packed file, of course
    return tar_file

@out.indent
def pack_local(files):
    #tell
    out.log('packing locally: ' + files, 'tar')

    #validate files
    if not validate_files(files):
        out.log('Error: files need to be given relative to www dir.', 'tar', out.LEVEL_ERROR)
        engine.quit()

    #register tar file
    tar_file = engine.get_new_local_file('tar')

    #assemble packing command. Always pack from www dir
    pack_command = 'tar cf ' + tar_file + ' --exclude .tar -C ' + engine.LOCAL_WWW_DIR + ' ' + files

    #pack!
    run.local(pack_command)

    #and return packed file, of course
    return tar_file

def pack_local_list(file_list):
    #tell
    out.log('packing locally a bunch of files', 'tar')

    #validate files
    if not validate_files_list(file_list):
        out.log('Error: files need to be given relative to www dir.', 'tar', out.LEVEL_ERROR)
        engine.quit()

    #register tar file
    tar_file = engine.get_new_local_file('tar')

    #register list file
    list_file_content = "\n".join(file_list)
    list_file = engine.write_local_file(list_file_content, 'files')

    #assemble packing command. Always pack from www dir
    pack_command = 'tar cf ' + tar_file + ' --files-from ' + list_file + ' -C ' + engine.LOCAL_WWW_DIR

    #pack!
    run.local(pack_command)

    #and return packed file, of course
    return tar_file


def unpack_local(archive):
    out.log('unpacking locally: ' + archive, 'tar')
    unpack_command = 'tar xf ' + archive + ' -C ' + engine.LOCAL_WWW_DIR
    run.local(unpack_command)

def unpack_remote(archive):
    out.log('unpacking on remote: ' + archive, 'tar')
    unpack_command = 'tar xf ' + archive + ' --warning=no-unknown-keyword -C ' + engine.REMOTE_WWW_DIR
    run.remote(unpack_command)

def validate_files_list(files_array):
    for file in files_array:
        if os.path.isabs(file):
            return False

    #no absolute path detected, we should be save now
    return True
def validate_files(files):
    return validate_files_list(files.split())
