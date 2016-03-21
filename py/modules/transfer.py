import engine
import run
import out

#writes the commands to file and executes the file. This way we circumvent all the escaping trouble.
@engine.cleanup_tmp_files
def execute_ftp_command(command, verbose = False):
    #write the command into file
    ftp_file = engine.write_local_file(command)
    #set verbose or not verbose
    if verbose:
        verbosity_option = '-v'
    else:
        verbosity_option = '-V'
    #run the ftp file
    run.local('ftp -i ' + verbosity_option + ' ftp://' + engine.FTP_USER + ':' + engine.FTP_PASSWORD + '@' + engine.FTP_HOST + ' <' + ftp_file)

@out.indent
def get(remote_file, local_file=None, verbose=False):
    #create new local file if not spcefied
    if local_file is None:
        local_file = engine.get_new_local_file()

    #print some info
    out.log("[Download] " + remote_file + " -> " + local_file, out.LEVEL_INFO)

    #get transfer system
    if engine.TRANSFER_SYSTEM == 'FTP':
        execute_ftp_command('get ' + remote_file + ' ' + local_file, verbose)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        out.log("Error: TRANSFER_SYSTEM SSH not implemented yet", out.LEVLE_ERROR)
    else:
        out.log("Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM, out.LEVEL_ERROR)

    #return new filename
    return local_file

def get_verbose(remote_file, local_file=None):
    return get(remote_file, local_file, True)

@out.indent
def put(local_file, remote_file=None, verbose=False):
    #create new remote file if none specified
    if remote_file is None:
        remote_file = engine.get_new_remote_file()

    #print some info
    out.log("[Upload] " + local_file + " -> " + remote_file, out.LEVEL_INFO)

    #choose correct transfer system
    if engine.TRANSFER_SYSTEM == 'FTP':
        execute_ftp_command('put ' + local_file + ' ' + remote_file, verbose)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        out.log("Error: TRANSFER_SYSTEM SSH not implemented yet", out.LEVEL_ERROR)
    else:
        out.log("Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM, out.LEVEL_ERROR)

    #return filename of uploaded file
    return remote_file

def put_verbose(local_file, remote_file=None):
    put(local_file, remote_file, True)

@out.indent
def remove_local(filename):
    out.log('[transfer] remove local file: ' + filename, out.LEVEL_INFO)
    run.local('rm ' + filename)

@out.indent
def remove_remote(filename):
    out.log('[transfer] remove remote file: ' + filename, out.LEVEL_INFO)
    command = 'delete ' + filename
    execute_ftp_command(command)

@out.indent
def remove_local_directory_contents(directoy):
    out.log('[transfer] remove content of local directory: ' + dircetory, out.LEVEL_INFO)
    run.local('rm ' + directory + '/*')

@out.indent
def remote_remote_directory_contents(directory):
    out.log('[transfer] remove content of remote directory: ' + dircetory, out.LEVEL_INFO)
    command = 'delete ' + directory + '/*'
    execute_ftp_command(command)

@out.indent
def local_move(from_file, to_file):
    out.log('[transfer] move local file: ' + from_file + ' -> ' + to_file)
    run.local('mv ' + from_file + ' ' + to_file)

@out.indent
def remote_move(from_file, to_file):
    out.log('[transfer] move remote file: ' + from_file + ' -> ' + to_file)
    command = 'rename ' + from_file + ' ' + to_file
    execute_ftp_command(command)

