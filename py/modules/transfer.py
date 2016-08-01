import engine
import run
import out
import gzip
import tar
import ftp

import os

@out.indent
def test_module():
    out.log("Testing FTP connection...", 'transfer')
    ftp.execute('pwd')


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
        ftp.execute(command)
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
        ftp.execute(command)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        out.log("Error: TRANSFER_SYSTEM SSH not implemented yet", 'upload', out.LEVEL_ERROR)
    else:
        out.log("Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM, 'upload', out.LEVEL_ERROR)

    #return filename of uploaded file
    return remote_file

def get_compressed(remote_file, local_file = None, verbose = False, permissions = None, fast_compression = False):
    #compress remote file
    compressed_remote = gzip.compress_remote(remote_file, fast=fast_compression)
    #download
    compressed_local = get(compressed_remote, gzip.compressed_filename(local_file), verbose, permissions)
    filesize = os.path.getsize(compressed_local)
    out.log('downloaded compressed ' + str(filesize/1000.0) + ' kb file', 'transfer')
    #restore uncompressed remote file
    gzip.uncompress_remote(compressed_remote)
    #uncmopress local file
    return gzip.uncompress_local(compressed_local, True)

@out.indent
def put_compressed(local_file, remote_file = None, verbose = False, permissions = None):
    #compress local file
    compressed_local = gzip.compress_local(local_file)
    #upload
    filesize = os.path.getsize(compressed_local)
    out.log('uploading compressed ' + str(filesize/1000.0) + ' kb file', 'transfer')
    compressed_remote = put(compressed_local, gzip.compressed_filename(remote_file), verbose, permissions)
    #restore local file
    gzip.uncompress_local(compressed_local)
    #uncompress remote file
    return gzip.uncompress_remote(compressed_remote, True)

#mirror complete directory recursively
def get_directory(directory):
    remote_tar = tar.pack_remote(directory)
    local_tar = get_compressed(remote_tar)
    tar.unpack_local(local_tar)

def put_directory(directory):
    local_tar = tar.pack_local(directory)
    remote_tar = put_compressed(local_tar)
    tar.unpack_remote(remote_tar)

@out.indent
def put_multiple(file_list):
    #split into ascii and non-ascii
    ascii_files, non_ascii_files = engine.split_by_encoding(file_list)

    #pack ascii files, upload compressed and unpack on server
    if len(ascii_files) > 0:
        out.log('uploading files with ascii compatible names', 'transfer')
        local_tar = tar.pack_local_list(ascii_files)
        remote_tar = put_compressed(local_tar)
        tar.unpack_remote(remote_tar)

    #take the non-ascii files and upload them one after another using ftp
    if len(non_ascii_files) > 0:
        out.log('uploading files with non-ascii filename', 'transfer')
        command = ''
        for f in non_ascii_files:
            command += u'put ' + engine.LOCAL_WWW_DIR + '/' + f + u' ' + ftp_path(f) + u'\n'
        ftp.execute(command)

def get_multiple(file_list):
    remote_tar = tar.pack_remote_list(file_list)
    local_tar = get_compressed(remote_tar, fast_compression = True)
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
    if engine.FTP_CLIENT == 'ftp':
        command = 'delete ' + ftp_path(filename)
    elif engine.FTP_CLIENT == 'sftp':
        command = 'rm ' + ftp_path(filename)
    else:
        out.log('Unknown ftp client ' + engine.FTP_CLIENT, 'transfer', out.LEVEL_ERROR)
        engine.quit()
    ftp.execute(command)

@out.indent
def remove_local_multiple(file_list):
    out.log('removing multiple local files', 'transfer')
    for file in file_list:
        run.local('rm "' + file + '"')

@out.indent
def remove_remote_multiple(file_list):
    out.log('removing multiple remote files', 'transfer')
    command = ''
    for file in file_list:
        if engine.FTP_CLIENT == 'ftp':
            command += 'delete ' + ftp_path(file) + '\n'
        elif engine.FTP_CLIENT == 'sftp':
            command += 'rm ' + ftp_path(file) + '\n'
        else:
            out.log('Unknown ftp client ' + engine.FTP_CLIENT, 'transfer', out.LEVEL_ERROR)
            engine.quit()
    ftp.execute(command)

@out.indent
def remove_local_directory_contents(directoy):
    out.log('remove content of local directory: ' + directory, 'transfer')
    run.local('rm ' + directory + '/*')

@out.indent
def remote_remote_directory_contents(directory):
    out.log('remove content of remote directory: ' + dircetory, 'transfer')
    if engine.FTP_CLIENT == 'ftp':
        command = 'delete ' + ftp_path(directory) + '/*'
    elif engine.FTP_CLIENT == 'sftp':
        command = 'rm ' + ftp_path(directory) + '/*'
    else:
        out.log('Unknown ftp client ' + engine.FTP_CLIENT, 'transfer', out.LEVEL_ERROR)
        engine.quit()
    ftp.execute(command)

@out.indent
def local_move(from_file, to_file):
    out.log('move local file: ' + from_file + ' -> ' + to_file, 'transfer')
    run.local('mv ' + from_file + ' ' + to_file)

@out.indent
def remote_move(from_file, to_file):
    out.log('move remote file: ' + from_file + ' -> ' + to_file, 'transfer')
    command = 'rename ' + ftp_path(from_file) + ' ' + ftp_path(to_file)
    ftp.execute(command)

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
    if engine.FTP_CLIENT == 'sftp':
        command = '-' + command
    if permissions is not None:
        command += "\nchmod " + str(permissions) + " " + ftp_path(directory)
    ftp.execute(command)

@out.indent
def remove_remote_directory(directory):
    out.log('remove remote directory: ' + directory, 'transfer')
    command = 'rmdir ' + ftp_path(directory)
    ftp.execute(command)

@out.indent
def set_local_mode(file, mode):
    out.log('setting mode ' + str(mode) + ' on ' + file, 'transfer')
    command = "chmod " + str(mode) + ' ' + file
    run.local(command)

@out.indent
def set_remote_mode(file, mode):
    out.log('setting mode ' + str(mode) + ' on ' + file, 'transfer')
    command = "chmod " + str(mode) + ' ' + ftp_path(file)
    ftp.execute(command)


def ftp_path(filename):
    return '"' + os.path.normpath(engine.FTP_WWW_DIR + '/' + filename) + '"'

def ssh_path(filename):
    return '"' + os.path.normpath(engine.SSH_WWW_DIR + '/' + filename) + '"'

def available():
    if engine.TRANSFER_SYSTEM == 'FTP':
        return engine.FTP_HOST is not None and engine.FTP_USER is not None and engine.FTP_PASSWORD is not None
    if engine.TRANSFER_SYSTEM == 'SSH':
        return False
    return False