import engine
import out
import run
import os
import fnmatch


@out.indent
def po():
    out.log('looking for .po files recursively...', 'compile')
    files = []
    for root, dirnames, filenames in os.walk(engine.LOCAL_WWW_DIR):
        for filename in fnmatch.filter(filenames, '*.po'):
            files.append(os.path.join(root, filename))

    for po in files:
        mo = po[:-3] + '.mo'
        # needs to be refreshed if
        # 1. there is no .mo file
        # 2. the .mo file is out of date
        # 3. the .mo file is not placed in a folder named 'orig'
        if (not os.path.isfile(mo) or os.path.getmtime(po) > os.path.getmtime(mo)) and (not os.path.split(os.path.dirname(po))[1] == 'orig'):
            out.log('compiling ' + po, 'compile')
            run.local('msgfmt -o ' + mo + ' ' + po)
        else:
            out.log('skipping ' + po, 'compile')

def less():
    run.local('cd ' + engine.LOCAL_MAKE_DIR + ' && make ' + engine.MAKEFILE_VARS + ' less', False)

def js():
    run.local('cd ' + engine.LOCAL_MAKE_DIR + ' && make ' + engine.MAKEFILE_VARS + ' js', False)

@out.indent
def all():
    out.log('compiling less files...', 'compile')
    less()
    out.log('compiling js files...', 'compile')
    js()
    out.log('compiling po files...', 'complete')
    po()