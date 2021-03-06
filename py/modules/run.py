import subprocess
import time
import os

import engine
import run
import out
import transfer
import php
import ssh

@out.indent
def test_module():
    out.log("Testing remote command...", 'run')
    run.remote('pwd', halt_on_output = False)
    out.log("Remote command has run successfully", 'run')

#run command locally. easy.
@out.indent
def local(command, halt_on_stderr = True, retry = 0, sudo = False, ignore_exit_code = False, halt_on_stdout = False):
    #tell what happens
    out.log(command, 'local', out.LEVEL_VERBOSE)

    #create output array
    output_array = []

    if sudo:
        out.log('prepending sudo to command', 'local', out.LEVEL_VERBOSE)
        command = 'sudo ' + command

    #run it using subprocess
    stderr_occured = False
    stdout_occured = False
    process = subprocess.Popen(command, shell = True, stdin = None, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    while process.poll() is None:
        read_something = False

        #read regular output
        output = process.stdout.readline()
        while output != '':
            read_something = True
            stdout_occured = True
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

        #if there was no output, wait a little bit for the program
        if not read_something and process.poll() is None:
            time.sleep(0.05)

    #get the exit code and print stuff if something has gone wrong
    exit_code = process.poll()
    if (not ignore_exit_code and exit_code != 0) or (halt_on_stderr and stderr_occured) or (halt_on_stdout and stdout_occured):
        if retry == 0:
            out.log("Error executing `" + str(command) + "`: Exit Code " + str(exit_code), 'local', out.LEVEL_ERROR)
            engine.quit()
        if retry > 0:
            out.log("Error executing `" + str(command) + "`. Retrying in " + str(engine.RETRY_TIMEOUT) + " seconds (" + str(retry) + " retries left)...", 'run', out.LEVEL_WARNING)
            time.sleep(engine.RETRY_TIMEOUT)
            local(command, halt_on_stderr, retry-1)
    if (ignore_exit_code and exit_code != 0):
        out.log("Error executing `" + str(command) + "`: Exit Code " + str(exit_code), 'local', out.LEVEL_ERROR)
        out.log("Do not quit because of previous error, because ignore_exit_code is set to True.", 'local', out.LEVEL_VERBOSE)

    return output_array


#run command on remote. a bit harder.
@out.indent
def remote(command, halt_on_output = False):
    #tell what happens
    out.log(command, 'remote', out.LEVEL_VERBOSE)

    #choose the correct command system
    if engine.COMMAND_SYSTEM == 'PHP':
        php.execute(command, halt_on_output)
    elif engine.COMMAND_SYSTEM == 'SSH':
        ssh.execute(command)
    else:
        #even less implemented
        out.log("Error Unknown COMMAND_SYSTEM " + engine.COMMAND_SYSTEM, 'remote', out.LEVEL_ERROR)
        engine.quit()

@out.indent
def remote_python_script(script_name, arguments = ''):
    #tell
    out.log('running python script ' + script_name, 'remote', out.LEVEL_VERBOSE)

    #upload script
    remote_script = transfer.put(script_name)

    #run
    remote('HOME=. python ' + remote_script + ' ' + arguments)

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

@out.indent
def remove_command_file():
    out.log('removing command file', 'run')
    try:
        engine.NORM_COMMAND_FILE
    except:
        out.log("Error: Could not find NORM_COMMAND_FILE. No file to remove", 'run', out.LEVEL_WARNING)
        return
    transfer.remove_remote(engine.NORM_COMMAND_FILE)




