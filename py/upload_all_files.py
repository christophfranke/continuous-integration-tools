from modules import engine
from modules import out
from modules import transfer

@engine.prepare_and_clean
def execute(filename = None):
    out.log("uploading all files from www directory...")
    #get/put directory is always relative to the www directory, so '.' just gets all
    transfer.put_directory('.')



def help():
    out.log("Uploading the complete www directory and copies it to your local www directory. Watch out, this command overwrites all files without asking.", 'help')