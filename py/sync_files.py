from modules import engine
from modules import out
from modules import transfer
from modules import sync

@engine.prepare_and_clean
def execute():
    out.log("Synchronizing remote files...")
    table = sync.download()



def help():
    out.log("This command donwloads all files, that are present on the remote but not on the local machines www dir.", 'help')