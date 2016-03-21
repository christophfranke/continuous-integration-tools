from modules import engine
from modules import run
from modules import out


@engine.prepare_and_clean
def execute(command):
    out.log("[command] executing " + command, out.LEVEL_INFO)
    run.remote(command)


def help():
    out.log("This command executes a shell command on the server and prints its output to console.", out.LEVEL_INFO)