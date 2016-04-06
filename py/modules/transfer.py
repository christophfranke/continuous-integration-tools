import engine
import run
import out
import gzip
import tar

import os

@out.indent
def test_module():
    out.log("Testing FTP connection...", 'transfer')
    execute_ftp_command('pwd')

#writes the commands to file and executes the file. This way we circumvent all the escaping trouble.
@engine.cleanup_tmp_files
def execute_ftp_command(command, verbose = False):
    #write the command into file
    ftp_file = engine.write_local_file(command, 'ftp')
    #set verbose or not verbose
    if verbose:
        out.log('The verbosity option for execute_command_file is currently not being used.','transfer', out.LEVEL_WARNING)
        verbosity_option = '-v'
    else:
        verbosity_option = '-V'

    #run the ftp file
    ftp_command_line = 'ftp -i ' + engine.FTP_PROTOCOL + '://' + escape(engine.FTP_USER) + ':' + escape(engine.FTP_PASSWORD) + '@' + engine.FTP_HOST + ' <' + ftp_file
    run.local(ftp_command_line)


@out.indent
def get(remote_file, local_file = None, verbose = False, permissions = None):
    #create new local file if not spcefied
    if local_file is None:
        #keep suffix
        suffix = engine.get_suffix(remote_file)
        local_file = engine.get_new_local_file(suffix)

    #print some info
    out.log(remote_file + " -> " + local_file, 'download')

    #get transfer system
    if engine.TRANSFER_SYSTEM == 'FTP':
        command = 'get ' + ftp_path(remote_file) + ' ' + local_file
        execute_ftp_command(command, verbose)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        out.log("Error: TRANSFER_SYSTEM SSH not implemented yet", 'download', out.LEVEL_ERROR)
        engine.quit()
    else:
        out.log("Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM, 'download', out.LEVEL_ERROR)
        engine.quit()

    #set permissions
    if permissions is not None:
        run.local('chmod ' + str(permissions) + ' ' + local_file)

    #return new filename
    return local_file

@out.indent
def put(local_file, remote_file = None, verbose = False, permissions = None):
    #create new remote file if none specified
    if remote_file is None:
        suffix = engine.get_suffix(local_file)
        remote_file = engine.get_new_remote_file(suffix)

    #print some info
    out.log(local_file + " -> " + remote_file, 'upload')

    #choose correct transfer system
    if engine.TRANSFER_SYSTEM == 'FTP':
        #put file
        command = 'put ' + local_file + ' ' + ftp_path(remote_file)
        #set permissions on remote
        if permissions is not None:
            command += "\nchmod " + str(permissions) + " " + ftp_path(remote_file)
        #...execute!
        execute_ftp_command(command, verbose)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        out.log("Error: TRANSFER_SYSTEM SSH not implemented yet", 'upload', out.LEVEL_ERROR)
    else:
        out.log("Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM, 'upload', out.LEVEL_ERROR)

    #return filename of uploaded file
    return remote_file

def get_compressed(remote_file, local_file = None, verbose = False, permissions = None):
    #compress remote file
    compressed_remote = gzip.compress_remote(remote_file)
    #download
    compressed_local = get(compressed_remote, gzip.compressed_filename(local_file), verbose, permissions)
    #restore uncompressed remote file
    gzip.uncompress_remote(compressed_remote)
    #uncmopress local file
    return gzip.uncompress_local(compressed_local, True)

def put_compressed(local_file, remote_file = None, verbose = False, permissions = None):
    #compress local file
    compressed_local = gzip.compress_local(local_file)
    #upload
    compressed_remote = put(compressed_local, gzip.compressed_filename(remote_file), verbose, permissions)
    #restore local file
    gzip.uncompress_local(compressed_local)
    #uncompress remote file
    return gzip.uncompress_remote(compressed_remote, True)

#mirror complete directory recursively
def get_directory(directory, verbose = False):
    remote_tar = tar.pack_remote(directory)
    local_tar = get_compressed(remote_tar, verbose = verbose)
    tar.unpack_local(local_tar)

def put_directory(directory, verbose = False):
    local_tar = tar.pack_local(directory)
    remote_tar = put_compressed(local_tar, verbose = verbose)
    tar.unpack_remote(remote_tar)

def put_multiple(file_list, verbose = False):
    local_tar = tar.pack_local_list(file_list)
    remote_tar = put_compressed(local_tar, verbose = verbose)
    tar.unpack_remote(remote_tar)

def get_multiple(file_list, verbose = False):
    remote_tar = tar.pack_remote_list(file_list)
    local_tar = get_compressed(remote_tar, verbose = verbose)
    tar.unpack_local(local_tar)

def put_verbose(local_file, remote_file=None):
    put(local_file, remote_file, True)

@out.indent
def remove_local(filename):
    out.log('remove local file: ' + filename, 'transfer')
    run.local('rm ' + filename)

@out.indent
def remove_remote(filename):
    out.log('remove remote file: ' + filename, 'transfer')
    command = 'delete ' + ftp_path(filename)
    execute_ftp_command(command)

@out.indent
def remove_local_directory_contents(directoy):
    out.log('remove content of local directory: ' + dircetory, 'transfer')
    run.local('rm ' + directory + '/*')

@out.indent
def remote_remote_directory_contents(directory):
    out.log('remove content of remote directory: ' + dircetory, 'transfer')
    command = 'delete ' + ftp_path(directory) + '/*'
    execute_ftp_command(command)

@out.indent
def local_move(from_file, to_file):
    out.log('move local file: ' + from_file + ' -> ' + to_file, 'transfer')
    run.local('mv ' + from_file + ' ' + to_file)

@out.indent
def remote_move(from_file, to_file):
    out.log('move remote file: ' + from_file + ' -> ' + to_file, 'transfer')
    command = 'rename ' + ftp_path(from_file) + ' ' + ftp_path(to_file)
    execute_ftp_command(command)

@out.indent
def create_local_directory(directory, permissions = None):
    out.log('create local directory: ' + directory, 'transfer')
    run.local('mkdir -p ' + directory)
    if permissions is not None:
        run.local('chmod ' + str(permissions) + ' ' + directory)

@out.indent
def create_remote_directory(directory, permissions = None):
    out.log('create remote directory: ' + directory, 'transfer')
    command = 'mkdir ' + ftp_path(directory)
    if permissions is not None:
        command += "\nchmod " + str(permissions) + " " + ftp_path(directory)
    execute_ftp_command(command)


def escape(s):
    escape_table = {
        '!':'%20',
        '"':'%22',
        '#':'%23',
        '$':'%24',
        '%':'%25',
        '&':'%26',
        "'":'%27',
        '(':'%28',
        ')':'%29',
        '*':'%2A',
        '+':'%2B',
        ',':'%2C',
        '-':'%2D',
        '.':'%2E',
        '/':'%2F',
        ':':'%3A',
        ';':'%3B',
        '<':'%3C',
        '=':'%3D',
        '>':'%3E',
        '?':'%3F',
        '@':'%40',
        '[':'%5B',
        '\\':'%5C',
        ']':'%5D',
        '^':'%5E',
        '`':'%60',
        '{':'%7B',
        '|':'%7C',
        '}':'%7D',
        '~':'%7E'
    }
    for character in escape_table:
        s = s.replace(character, escape_table[character])

    return s

def ftp_path(filename):
    return os.path.normpath(engine.FTP_WWW_DIR + '/' + filename)

def ssh_path(filename):
    return os.path.normpath(engine.SSH_WWW_DIR + '/' + filename)
