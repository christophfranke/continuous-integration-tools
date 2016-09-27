from modules import engine
from modules import out
from modules import run

@engine.prepare_and_clean
def execute():
    out.log("showing tail of apache error log file...")
    run.local('tail -n 10 ' + engine.LOCAL_APACHE_ERROR_LOG)



def help():
    out.log("This command is a more rememberable shortcut for outputting the last 10 lines of the apache error log file.", 'help')