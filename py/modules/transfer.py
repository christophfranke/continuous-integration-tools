import engine
import run
import out
import gzip

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
    if verbose and False: #never show anything, this basically clutters the output and makes it less readable
        verbosity_option = '-v'
    else:
        verbosity_option = '-V'

    #run the ftp file
    run.local('ftp -i ' + verbosity_option + ' ftp://' + engine.FTP_USER + ':' + engine.FTP_PASSWORD + '@' + engine.FTP_HOST + ' <' + ftp_file)

    #output an error if this file is not empty
    #if engine.local_is_not_empty(ftp_error_log):
    #    out.log('There had been an error with the last ftp command.', 'ftp', out.LEVEL_ERROR)
    #    out.file(ftp_error_log, 'ftp', out.LEVEL_ERROR)
    #    exit()


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
        command = 'get ' + remote_file + ' ' + local_file
        execute_ftp_command(command, verbose)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        out.log("Error: TRANSFER_SYSTEM SSH not implemented yet", 'download', out.LEVLE_ERROR)
    else:
        out.log("Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM, 'download', out.LEVEL_ERROR)

    #set permissions
    if permissions is not None:
        run.local('chmod ' + str(permissions) + ' ' + local_file)

    #return new filename
    return local_file

def get_verbose(remote_file, local_file=None):
    return get(remote_file, local_file, True)

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
        command = 'put ' + local_file + ' ' + remote_file
        #set permissions on remote
        if permissions is not None:
            command += "\nchmod " + str(permissions) + " " + remote_file
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

def put_verbose(local_file, remote_file=None):
    put(local_file, remote_file, True)

@out.indent
def remove_local(filename):
    out.log('remove local file: ' + filename, 'transfer')
    run.local('rm ' + filename)

@out.indent
def remove_remote(filename):
    out.log('remove remote file: ' + filename, 'transfer')
    command = 'delete ' + filename
    execute_ftp_command(command)

@out.indent
def remove_local_directory_contents(directoy):
    out.log('remove content of local directory: ' + dircetory, 'transfer')
    run.local('rm ' + directory + '/*')

@out.indent
def remote_remote_directory_contents(directory):
    out.log('remove content of remote directory: ' + dircetory, 'transfer')
    command = 'delete ' + directory + '/*'
    execute_ftp_command(command)

@out.indent
def local_move(from_file, to_file):
    out.log('move local file: ' + from_file + ' -> ' + to_file, 'transfer')
    run.local('mv ' + from_file + ' ' + to_file)

@out.indent
def remote_move(from_file, to_file):
    out.log('move remote file: ' + from_file + ' -> ' + to_file, 'transfer')
    command = 'rename ' + from_file + ' ' + to_file
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
    command = 'mkdir ' + directory
    if permissions is not None:
        command += "\nchmod " + str(permissions) + " " + directory
    execute_ftp_command(command)