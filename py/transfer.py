import engine
import run

#writes the commands to file and executes the file. This way we circumvent all the escaping trouble.
def execute_ftp_command(command, verbose):
    #write the command into file
    ftp_file = engine.write_local_file(command)
    #set verbose or not verbose
    if verbose:
        verbosity_option = '-v'
    else:
        verbosity_option = '-V'
    #run the ftp file
    run.local('ftp -i ' + verbosity_option + ' ftp://' + engine.FTP_USER + ':' + engine.FTP_PASSWORD + '@' + engine.FTP_HOST + ' <' + ftp_file)


def get(remote_file, local_file=None, verbose=False):
    #create new local file if not spcefied
    if local_file is None:
        local_file = engine.get_new_local_file()

    #print some info
    print "[Download] " + remote_file + " -> " + local_file

    #get transfer system
    if engine.TRANSFER_SYSTEM == 'FTP':
        execute_ftp_command('get ' + remote_file + ' ' + local_file, verbose)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        print "Error: TRANSFER_SYSTEM SSH not implemented yet"
    else:
        print "Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM

    #return new filename
    return local_file

def get_verbose(remote_file, local_file=None):
    return get(remote_file, local_file, True)

def put(local_file, remote_file=None, verbose=False):
    #create new remote file if none specified
    if remote_file is None:
        remote_file = engine.get_new_remote_file()

    #print some info
    print "[Upload] " + local_file + " -> " + remote_file

    #choose correct transfer system
    if engine.TRANSFER_SYSTEM == 'FTP':
        execute_ftp_command('put ' + local_file + ' ' + remote_file, verbose)
    elif engine.TRANSFER_SYSTEM == 'SSH':
        print "Error: TRANSFER_SYSTEM SSH not implemented yet"
    else:
        print "Error: Unknown TRANSFER_SYSTEM " + engine.TRANSFER_SYSTEM

    #return filename of uploaded file
    return remote_file

def put_verbose(local_file, remote_file=None):
    put(local_file, remote_file, True)