import engine
import run
import out
import buffering


#writes the commands to file and executes the file. This way we circumvent all the escaping trouble.
@buffering.buffered
@out.indent
def execute(command):
    out.log('executing ' + command, 'ftp', out.LEVEL_VERBOSE)
    #write the command into file
    ftp_file = engine.write_local_file(command, 'ftp')

    #run the ftp file
    if engine.FTP_CLIENT == 'ftp':
        ftp_command_line = 'ftp -i ' + engine.FTP_PROTOCOL + '://' + engine.escape(engine.FTP_USER) + ':' + engine.escape(engine.FTP_PASSWORD) + '@' + engine.FTP_HOST + ' <' + ftp_file
    elif engine.FTP_CLIENT == 'sftp':
        ftp_command_line = 'sftp -b ' + ftp_file + ' ' + engine.escape(engine.FTP_USER) + '@' + engine.FTP_HOST
    run.local(ftp_command_line, retry = 3)


#setup and expose buffering interface
execute.set_name('ftp')
def start_buffer():
    execute.start_buffer()
def flush_buffer():
    execute.flush_buffer()
def end_buffer():
    execute.end_buffer();