from modules import engine
from modules import out
from modules import run
from modules import php
from time import sleep

@engine.prepare_and_clean
def execute():
    #make sure we have the php command file online
    php.upload_command_file()
    #open it with the phpinfo parameter
    run.local('open ' + engine.REMOTE_COMMAND_URL + '?phpinfo')
    #give the browser some time to open the url before deleting the underlying file
    sleep(5)


def help():
    out.log("Open the phpinfo output of the remote in your browser.", 'help')