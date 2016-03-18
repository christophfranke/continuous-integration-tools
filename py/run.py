import os
import engine
import run


#run command locally. easy.
def local(command):
    #tell what happens
    print "[local] " + command
    #run it
    exit_code = os.system(command)

    #check for exitcode
    if exit_code != 0:
        print "Error executing `" + str(command) + "`: Exit Code " + str(exit_code)
        exit()

#run command on remote. a bit harder.
def remote(command):
    #tell what happens
    print "[remote] " + command

    #write command to file and upload it
    script_content = '#!/bin/bash\n' + command
    filename = engine.write_remote_file(script_content)

    #choose the correct command system
    if engine.COMMAND_SYSTEM == 'PHP':
        run.local('curl ' + engine.REMOTE_COMMAND_FILE + '?file=' + filename)
    elif engine.COMMAND_SYSTEM == 'SSH':
        print "Error: COMMAND_SYSTEM SSH not implemented yet"
    else:
        print "Error Unknown COMMAND_SYSTEM " + engine.COMMAND_SYSTEM
