from modules import engine
from modules import out
from modules import transfer

@engine.prepare_and_clean
def execute(filename = None):
    out.log("downloading all files from www directory...")
    #watch out: we need to specify the directory here relatively to the root directory. do not (!) use absolute paths
    transfer.get_directory(engine.WWW_DIR)



def help():
    out.log("Downloads the complete www directory and copies it to your local www directory. Watch out, this command overwrites all files without asking.", 'help')