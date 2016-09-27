from modules import engine
from modules import run
from modules import out

@engine.prepare_and_clean
def execute():
    out.log("uploading command file...")
    run.upload_command_file()


def help():
    out.log("This command updates the command file, since it is not really handy to update that manually.", 'help')