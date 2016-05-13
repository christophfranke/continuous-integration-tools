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
    ftp_command_line = 'ftp -i ' + engine.FTP_PROTOCOL + '://' + engine.escape(engine.FTP_USER) + ':' + engine.escape(engine.FTP_PASSWORD) + '@' + engine.FTP_HOST + ' <' + ftp_file
    run.local(ftp_command_line, retry = 3)

