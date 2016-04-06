from modules import engine
from modules import out
from modules import transfer

@engine.prepare_and_clean
def execute():
    out.log("downloading all files from www directory...")
    sync.download(True, False)



def help():
    out.log("Downloads the complete www directory and copies it to your local www directory. Watch out, this command overwrites all files without asking.", 'help')