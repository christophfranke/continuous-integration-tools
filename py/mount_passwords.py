from modules import engine
from modules import out
from modules import run

@engine.prepare_and_clean
def execute():
    out.log("Mounting passwords...")
    run.local('mkdir -p ' + engine.PASSWORD_DIRECTORY)
    run.local('chmod 700 ' + engine.PASSWORD_DIRECTORY)
    run.local('sshfs macmini@Mac-minis-Mac-mini.local:Zugangsdaten ' + engine.PASSWORD_DIRECTORY + ' -o volname=Zugangsdaten')



def help():
    out.log("Mount the passwords that are stored on a remote machine.", 'help')