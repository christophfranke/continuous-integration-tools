from modules import engine
from modules import out
from modules import apache

@engine.prepare_and_clean
def execute(mode = None):
    out.log('setting up domain lookup and virtual server')
    apache.append_to_hosts()
    apache.append_to_server_config()
    apache.restart()



def help():
    out.log("Setup your local domain.", 'help')
