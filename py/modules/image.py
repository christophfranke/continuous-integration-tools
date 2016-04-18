import out
import engine
import run

import os
import fnmatch


#depends on jpegoptim and optipng


@out.indent
def optimize_jpg():
    out.log('optimizing jpgs...', 'image')
    for root, dirnames, filenames in os.walk(engine.LOCAL_WWW_DIR):
        for filename in fnmatch.filter(filenames, '*.jpg'):
            run.local('jpegoptim ' + root + '/' + filename)

@out.indent
def optimize_png():
    out.log('optimizing pngs...', 'image')
    for root, dirnames, filenames in os.walk(engine.LOCAL_WWW_DIR):
        for filename in fnmatch.filter(filenames, '*.png'):
            original_name = root + '/' + filename
            optimized_name = root + '/' + filename[:-4] + 'opt.png'
            run.local('pngcrush ' + original_name + ' ' + optimized_name, halt_on_stderr = False)
            if os.path.isfile(optimized_name):
                run.local('rm ' + original_name)
                run.local('mv ' + optimized_name + ' ' + original_name)

