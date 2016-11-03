import engine
import out
import transfer
import buffering
import os


command_file_ready = False

@buffering.buffered
@out.indent
def execute(command, halt_on_output = False):
    import run

    #tell
    out.log(command, 'php', out.LEVEL_VERBOSE)

    #make sure the command file is online
    upload_command_file()

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

    #execute all buffered ftp commands
    engine.sync_ftp()

    #and go
    run.local(curl_command, halt_on_stdout = halt_on_output) #halt_on_output strongly depends on the command

    #log output to screen
    if halt_on_output:
        log_level = out.LEVEL_ERROR
        if os.stat(output_file).st_size > 0:
            out.file(output_file, 'php exec', out.LEVEL_ERROR)
            out.log('error executing "' + command + '" via php command system.', 'php', out.LEVEL_ERROR)
            engine.quit()

    out.file(output_file, 'php exec', out.LEVEL_INFO)
    return output_file

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
    out.log('removing command file', 'php', out.LEVEL_VERBOSE)
    try:
        engine.NORM_COMMAND_FILE
    except:
        out.log("Error: Could not find NORM_COMMAND_FILE. No file to remove", 'php', out.LEVEL_WARNING)
        return
    transfer.remove_remote(engine.NORM_COMMAND_FILE)
    command_file_ready = False

#setup and expose buffering interface
execute.set_name('php')
def start_buffer():
    execute.start_buffer()
def flush_buffer():
    execute.flush_buffer()
def end_buffer():
    execute.end_buffer();
def has_buffer():
    return execute.has_buffer()

