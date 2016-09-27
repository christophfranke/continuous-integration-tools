from modules import engine
from modules import out

@engine.prepare_and_clean
def execute():
    out.log('setting up remote...')
    engine.initialize()


def help():
    out.log("initializes everything necessary for all systems to work.", 'help') # <- this is a real vague and probably wrong help text