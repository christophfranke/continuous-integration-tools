import engine
import run
import out

#writes the commands to file and executes the file. This way we circumvent all the escaping trouble.
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

