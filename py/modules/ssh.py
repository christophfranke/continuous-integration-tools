import engine
import out

#executes a command via ssh
@out.indent
def execute(command):
    import run
    #out.log('executing ' + command, 'ssh', out.LEVEL_VERBOSE)

    #run the command
    ssh_command_line = 'ssh ' + engine.SSH_USER + '@' + engine.SSH_HOST + " 'cd " + engine.SSH_PATH_TO_WWW_DIR + ' && ' + command + "'"
    run.local(ssh_command_line, retry = 3, halt_on_stderr = False)


def add_key_to_server():
    import run
    import transfer

    key_file = transfer.put('~/.ssh/id_rsa.pub')
    run.remote('mkdir -p ~/.ssh')
    run.remote('cat ' + key_file + ' >> ~/.ssh/authorized_keys')
