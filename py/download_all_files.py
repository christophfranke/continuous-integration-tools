from modules import engine
from modules import out
from modules import transfer

@engine.prepare_and_clean
def execute(filename = None):
    out.log("downloading all files from www directory...")
    #get directory is always relative to the www directory, so '.' just gets all
    sync.download(True)



def help():
    out.log("Downloads the complete www directory and copies it to your local www directory. Watch out, this command overwrites all files without asking.", 'help')