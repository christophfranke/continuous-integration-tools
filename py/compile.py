from modules import engine
from modules import out
from modules import run
from modules import compile


@engine.prepare_and_clean
def execute(types = None):

    #compile all by default
    if types is None:
        types = 'all'

    #compile po
    if types == 'all' or types == 'po':
        out.log('compiling mo files')
        compile.po()

    #if that was our only job we are done here
    if types == 'po':
        return

    #check for enabled build system
    if not engine.ENABLE_BUILD_SYSTEM:
        out.log('The build system is not enabled. Make sure you have set the ENABLE_BUILD_SYSTEM set to True in your config. Also note, that you will have to specify a SRC_URL and a BUILD_URL in you project config.', 'command', out.LEVEL_ERROR)
        return

    #compile less
    if types == 'all' or types == 'less':
        out.log('compiling less files...')
        compile.less()

    #compile js
    if types == 'all' or types == 'js':
        out.log('compiling js files')
        compile.js()


def help():
    out.log('Compiles less, js and mo files. Takes a parameter specifying what to compile, options are less, js, po, all (default).', 'help')