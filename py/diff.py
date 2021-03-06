from modules import engine
from modules import out
from modules import sync

@engine.prepare_and_clean
def execute(mode = None):
    out.log('Diff between local files and remote files...')
    sync.diff()



def help():
    out.log("Compares all local and all server files and prints a detailed log.", 'help')
