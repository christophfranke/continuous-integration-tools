from modules import engine
from modules import out
from modules import run

@engine.prepare_and_clean
def execute():
    run.local('open ' + engine.REMOTE_COMMAND_URL + '?phpinfo')

def help():
    out.log("Open the phpinfo output of the remote in your browser.", 'help')