import os
import engine
import run
import out
import transfer


#run command locally. easy.
@out.indent
def local(command):
    #tell what happens
    out.log("[local] " + command, out.LEVEL_INFO)
    #run it
    exit_code = os.system(command)

    #check for exitcode
    if exit_code != 0:
        out.log("Error executing `" + str(command) + "`: Exit Code " + str(exit_code), out.LEVEL_ERROR)
        exit()

#run command on remote. a bit harder.
@out.indent
@engine.cleanup_tmp_files
def remote(command):
    #tell what happens
    out.log("[remote] " + command, out.LEVEL_INFO)

    #write command to file and upload it
    script_content = '#!/bin/bash\n' + command
    filename = engine.write_remote_file(script_content)

    #choose the correct command system
    if engine.COMMAND_SYSTEM == 'PHP':
        run.local('curl ' + engine.REMOTE_COMMAND_URL + '?file=' + filename + "\&indent=" + str(out.indentation))
    elif engine.COMMAND_SYSTEM == 'SSH':
        out.log("Error: COMMAND_SYSTEM SSH not implemented yet", out.LEVEL_ERROR)
    else:
        out.log("Error Unknown COMMAND_SYSTEM " + engine.COMMAND_SYSTEM, out.LEVEL_ERROR)

#make sure the command file is online and everything is setup correctly. this funciton will be called automatically, if there is no security hash set in the project config
@out.indent
def upload_command_file():
    #look for existing hash
    try:
        engine.REMOTE_ROOT_URL
    except AttributeError:
        out.log("[run] Error: Could not upload command file, because REMOTE_HTTP_ROOT is undefined. Make sure you have all necessary information in your project config.")
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
