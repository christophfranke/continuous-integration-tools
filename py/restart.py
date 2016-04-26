from modules import engine
from modules import out
from modules import run
from modules import apache

@engine.prepare_and_clean
def execute():
    out.log("restarting apache server...")
    apache.restart()



def help():
    out.log("Restarts the apache server.", 'help')