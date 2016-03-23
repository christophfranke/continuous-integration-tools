import subprocess
import time

import engine
import run
import out
import transfer


@out.indent
def test_module():
    out.log("Testing local command...", 'local')
    run.local('pwd')
    out.log("Testing remote command...", 'local')
    run.remote('pwd')

#run command locally. easy.
@out.indent
def local(command):
    #tell what happens
    out.log(command, 'local', out.LEVEL_VERBOSE)

    #run it
    #exit_code = os.system(command)

    #run it using subprocess
    process = subprocess.Popen(command, shell = True, stdin = None, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    while process.poll() is None:
        output = process.stdout.readline()
        error = process.stderr.readline()
        if output != '':
            out.log(output, 'local')
        if error != '':
            out.log(error, 'local', out.LEVEL_ERROR)
        time.sleep(0.05)
    exit_code = process.poll()

    #check for exitcode
    if exit_code != 0:
        out.log("Error executing `" + str(command) + "`: Exit Code " + str(exit_code), 'local', out.LEVEL_ERROR)
        exit()

#run command on remote. a bit harder.
@out.indent
@engine.cleanup_tmp_files
def remote(command):
    #tell what happens
    out.log(command, 'remote', out.LEVEL_VERBOSE)

    #write command to file and upload it
    script_content = '#!/bin/bash\n' + command
    filename = engine.write_remote_file(script_content, 'sh', permissions = '777')

    #choose the correct command system
    if engine.COMMAND_SYSTEM == 'PHP':
        #reserve a remote .txt file
        output_file = engine.get_new_local_file('log', True);
        #run the command via php access and tell the server to put the commands output into the remote output file
        run.local('curl --silent --output ' + output_file + ' ' + engine.REMOTE_COMMAND_URL + '?cmd=' + filename)
        #log output to screen
        out.file(output_file, 'php exec')
    elif engine.COMMAND_SYSTEM == 'SSH':
        out.log("Error: COMMAND_SYSTEM SSH not implemented yet", 'remote', out.LEVEL_ERROR)
    else:
        out.log("Error Unknown COMMAND_SYSTEM " + engine.COMMAND_SYSTEM, 'remote', out.LEVEL_ERROR)

#make sure the command file is online and everything is setup correctly. this funciton will be called automatically, if there is no security hash set in the project config
@out.indent
def upload_command_file():
    #look for existing hash
    try:
        engine.REMOTE_ROOT_URL
    except AttributeError:
        out.log("Error: Could not upload command file, because REMOTE_HTTP_ROOT is undefined. Make sure you have all necessary information in your project config.", 'run', out.LEVEL_ERROR)
        return False
    try:
        engine.REMOTE_COMMAND_FILE
    except AttributeError:
        new_hash = engine.get_random_secury_id()
        engine.add_config('SECURITY_HASH', new_hash)
        engine.REMOTE_COMMAND_FILE = os.path.normpath(engine.REMOTE_ROOT_DIR + '/' + engine.SECURITY_HASH + '.php')
        engine.REMOTE_COMMAND_URL = engine.REMOTE_ROOT_URL + '/' + engine.SECURITY_HASH + '.php'

    transfer.put('php/cmd.php', engine.REMOTE_COMMAND_FILE)
    return True
