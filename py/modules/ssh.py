import engine

#executes a command via ssh
@out.indent
def execute(command):
    import run
    out.log('executing ' + command, 'ssh', out.LEVEL_VERBOSE)
    out.log('not yet implemented', 'ssh', out.LEVEL_ERROR)
    engine.quit()

    #run the command
    ssh_command_line = 'ssh ' + escape(engine.SSH_USER) + ':' + escape(engine.SSH_PASSWORD) + '@' + engine.SSH_HOST + ' ' + command
    run.local(ssh_command_line)

