import subprocess
import time
import os

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
def local(command, halt_on_stderr = True, retry = 0, sudo = False):
    #tell what happens
    out.log(command, 'local', out.LEVEL_VERBOSE)

    #create output array
    output_array = []

    if sudo:
        out.log('prepending sudo to command', 'local', out.LEVEL_VERBOSE)
        command = 'sudo ' + command

    #run it using subprocess
    stderr_occured = False
    process = subprocess.Popen(command, shell = True, stdin = None, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    while process.poll() is None:
        read_something = False

        #read regular output
        output = process.stdout.readline()
        while output != '':
            read_something = True
            out.log(output, 'local')
            output_array.append(output)
            output = process.stdout.readline()

        #read error output
        error = process.stderr.readline()
        while error != '':
            if retry == 0:
                out.log(error, 'local', out.LEVEL_ERROR)
            else:
                out.log(error, 'local', out.LEVEL_VERBOSE)
            stderr_occured = True
            read_something = True
            error = process.stderr.readline()

        #if there was no output, wait a little bit for the programm to finish
        if not read_something and process.poll() is None:
            time.sleep(0.05)

    #get the exit code and print stuff if something has gone wrong
    exit_code = process.poll()
    if exit_code != 0 or (halt_on_stderr and stderr_occured):
        if retry == 0:
            out.log("Error executing `" + str(command) + "`: Exit Code " + str(exit_code), 'local', out.LEVEL_ERROR)
            engine.quit()
        if retry > 0:
            out.log("Error executing `" + str(command) + "`. Retrying in " + str(engine.RETRY_TIMEOUT) + " seconds (" + str(retry) + " tries left)...", 'run', out.LEVEL_WARNING)
            time.sleep(engine.RETRY_TIMEOUT)
            local(command, halt_on_stderr, retry-1)

    return output_array


#run command on remote. a bit harder.
@out.indent
@engine.cleanup_tmp_files
def remote(command):
    #tell what happens
    out.log(command, 'remote', out.LEVEL_VERBOSE)

    #write command to file and upload it. We do it this way, althouth this is quite inefficient, but otherwise we'd have tremendous problems with escaping characters.
    #althouth, TODO: escape special characters in command
    script_content = '#!/bin/bash\n' + command
    filename = engine.write_remote_file(script_content, 'sh', permissions = '777')

    #choose the correct command system
    if engine.COMMAND_SYSTEM == 'PHP':
        #reserve a remote .log file
        output_file = engine.get_new_local_file('log', True);
        #run the command via php access and tell the server to put the commands output into the remote output file
        curl_command = 'curl --silent --output ' + output_file
        #account for basic auth
        if engine.NEED_BASIC_AUTH:
            curl_command += ' -u ' + engine.AUTH_USER + ':' + engine.AUTH_PASSWORD
        #continue assembling curl command
        curl_command += ' ' + engine.REMOTE_COMMAND_URL + '?cmd=' + filename
        #and go
        run.local(curl_command, False) #False indicates, that we do not treat any output on stderr as error, because curl uses this for showing additional non-error information
        #log output to screen
        out.file(output_file, 'php exec')
    elif engine.COMMAND_SYSTEM == 'SSH':
        #not implemented
        out.log("Error: COMMAND_SYSTEM SSH not implemented yet", 'remote', out.LEVEL_ERROR)
        engine.quit()
    else:
        #even less implemented
        out.log("Error Unknown COMMAND_SYSTEM " + engine.COMMAND_SYSTEM, 'remote', out.LEVEL_ERROR)
        engine.quit()

@out.indent
@engine.cleanup_tmp_files
def remote_python_script(script_name, arguments = ''):
    #tell
    out.log('running python script ' + script_name, 'remote', out.LEVEL_VERBOSE)

    #upload script
    remote_script = transfer.put(script_name)

    #run
    remote('python ' + remote_script + ' ' + arguments)

#make sure the command file is online and everything is setup correctly. this funciton will be called automatically, if COMMAND_SYSTEM_READY is not  set in the project config
@out.indent
def upload_command_file():
    #look for existing hash
    try:
        engine.REMOTE_ROOT_URL
    except AttributeError:
        out.log("Error: Could not upload command file, because REMOTE_HTTP_ROOT is undefined. Make sure you have all necessary information in your project config.", 'run', out.LEVEL_ERROR)
        engine.quit()
    try:
        engine.NORM_COMMAND_FILE
    except AttributeError:
        new_hash = engine.get_random_secury_id()
        engine.add_config('SECURITY_HASH', new_hash)
        engine.NORM_COMMAND_FILE = os.path.normpath(engine.SECURITY_HASH + '.php')
        engine.REMOTE_COMMAND_URL = engine.REMOTE_ROOT_URL + '/' + engine.NORM_COMMAND_FILE

    out.log('uploading command file to ' + engine.NORM_COMMAND_FILE, 'run')
    transfer.put(engine.SCRIPT_DIR + '/php/cmd.php', engine.NORM_COMMAND_FILE)
