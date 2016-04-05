from modules import engine
from modules import out

@engine.prepare_and_clean
def execute(key = None):
    out.log('These are all configuration settings.')
    config_vars = engine.get_config()
    for k in config_vars:
        out.log(k + ' = ' + str(config_vars[k]))

def help():
    out.log("This command will print all the variables, that are set in the engines environment that look like config variables.", 'help')