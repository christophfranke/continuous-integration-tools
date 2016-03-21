import os
import engine
import run
import out


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
def remote(command):
    #tell what happens
    out.log("[remote] " + command, out.LEVEL_INFO)

    #write command to file and upload it
    script_content = '#!/bin/bash\n' + command
    filename = engine.write_remote_file(script_content)

    #choose the correct command system
    if engine.COMMAND_SYSTEM == 'PHP':
        run.local('curl ' + engine.REMOTE_COMMAND_FILE + '?file=' + filename)
    elif engine.COMMAND_SYSTEM == 'SSH':
        out.log("Error: COMMAND_SYSTEM SSH not implemented yet", out.LEVEL_ERROR)
    else:
        out.log("Error Unknown COMMAND_SYSTEM " + engine.COMMAND_SYSTEM, out.LEVEL_ERROR)
