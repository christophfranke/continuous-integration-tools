import engine
import out
import run
import os
import fnmatch


@out.indent
def po():
    out.log('looking for .po files recursively...', 'compile', out.LEVEL_VERBOSE)
    compiled_files = 0
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
            compiled_files += 1
        else:
            out.log('skipping ' + po, 'compile', out.LEVEL_VERBOSE)

    out.log('all .mo files up to date.', 'compile')

def less():
    run.local('cd ' + engine.LOCAL_MAKE_DIR + ' && make ' + engine.MAKEFILE_VARS + ' less', False)
    md5_file = append_md5(engine.path_join(engine.BUILD_URL, 'style.css'), copy_zipped = True)
    save_to_php(engine.LOCAL_WWW_DIR + '/' + engine.CSS_INCLUDE_FILE, engine.force_absolute(md5_file))


def js():
    run.local('cd ' + engine.LOCAL_MAKE_DIR + ' && make ' + engine.MAKEFILE_VARS + ' js', False)
    md5_file = append_md5(engine.path_join(engine.BUILD_URL, '/main.js'), copy_zipped = True)
    save_to_php(engine.LOCAL_WWW_DIR + '/' + engine.JS_INCLUDE_FILE, engine.force_absolute(md5_file))

@out.indent
def all():
    out.log('compiling less files...', 'compile')
    less()
    out.log('compiling js files...', 'compile')
    js()
    out.log('compiling po files...', 'complete')
    po()

#copies the file and appends its md5sum
#we could use a symlink, but some hosts don't like that
def append_md5(filename, copy_zipped = False):
    suffix = engine.get_suffix(filename)
    base = filename[:-len(suffix)]
    md5hash = engine.md5sum(engine.path_join(engine.LOCAL_WWW_DIR, filename))

    new_filename = base + md5hash + '.' + suffix

    run.local('cd ' + engine.LOCAL_WWW_DIR + ' && cp ' + engine.force_relative(filename) + ' ' + engine.force_relative(new_filename))
    if copy_zipped:
        run.local('cd ' + engine.LOCAL_WWW_DIR + ' && cp ' + engine.force_relative(filename) + '.gz ' + engine.force_relative(new_filename) + '.gz')

    return new_filename
    
#saves a variable to file
def save_to_php(filename, data):
    content = "<?php return "
    if type(data) == str:
        content += "'" + data + "';"
    else:
        out.log('save_to_php does not support type ' + str(type(data)) + '.', 'compile', out.LEVEL_ERROR)
        engine.quit()

    file.write_local(content, filename = filename)

