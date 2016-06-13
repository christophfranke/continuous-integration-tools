import engine
import out
import transfer


command_file_ready = False

@out.indent
def execute(command, halt_on_output = True):
    import run
    upload_command_file()

    #tell
    out.log('executing ' + command, 'php', out.LEVEL_VERBOSE)

    #write command to file and upload it. We do it this way, althouth this is quite inefficient, but otherwise we'd have tremendous problems with escaping characters.
    #althouth, TODO: escape special characters in command
    script_content = '#!/bin/bash\n' + command
    filename = engine.write_remote_file(script_content, 'sh', permissions = '777')

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
    run.local(curl_command, halt_on_output) #halt_on_output strongly depends on the command

    #log output to screen
    out.file(output_file, 'php exec')

    return

#make sure the command file is online and everything is setup correctly. this funciton will be called automatically, if COMMAND_SYSTEM_READY is not  set in the project config
@out.indent
def upload_command_file():
    global command_file_ready
    if command_file_ready:
        return
    #look for existing hash
    try:
        engine.REMOTE_ROOT_URL
    except AttributeError:
        out.log("Error: Could not upload command file, because REMOTE_HTTP_ROOT is undefined. Make sure you have all necessary information in your project config.", 'php', out.LEVEL_ERROR)
        engine.quit()
    try:
        engine.NORM_COMMAND_FILE
    except AttributeError:
        new_hash = engine.get_random_secury_id()
        engine.add_config('SECURITY_HASH', new_hash)
        engine.NORM_COMMAND_FILE = os.path.normpath(engine.SECURITY_HASH + '.php')
        engine.REMOTE_COMMAND_URL = engine.REMOTE_ROOT_URL + '/' + engine.NORM_COMMAND_FILE

    out.log('uploading command file to ' + engine.NORM_COMMAND_FILE, 'php')
    transfer.put(engine.SCRIPT_DIR + '/php/cmd.php', engine.NORM_COMMAND_FILE)
    command_file_ready = True

@out.indent
def remove_command_file():
    global command_file_ready
    if not command_file_ready:
        return
    out.log('removing command file', 'php')
    try:
        engine.NORM_COMMAND_FILE
    except:
        out.log("Error: Could not find NORM_COMMAND_FILE. No file to remove", 'php', out.LEVEL_WARNING)
        return
    transfer.remove_remote(engine.NORM_COMMAND_FILE)


