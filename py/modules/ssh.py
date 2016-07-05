import engine
import out

#executes a command via ssh
@out.indent
def execute(command):
    import run
    #out.log('executing ' + command, 'ssh', out.LEVEL_VERBOSE)

    #run the command
    #ssh_command_line = 'ssh ' + engine.escape(engine.SSH_USER) + ':' + engine.escape(engine.SSH_PASSWORD) + '@' + engine.SSH_HOST + " '" + command + "'"
    ssh_command_line = 'ssh ' + engine.SSH_USER + '@' + engine.SSH_HOST + " 'cd " + engine.SSH_PATH_TO_WWW_DIR + ' && ' + command + "'"
    run.local(ssh_command_line, retry = 3)

