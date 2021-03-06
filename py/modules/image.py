import out
import engine
import run

import os
import fnmatch


#depends on jpegoptim and optipng


@out.indent
def optimize_jpg(quality = 100):
    out.log('optimizing jpgs...', 'image')
    for root, dirnames, filenames in os.walk(engine.LOCAL_WWW_DIR):
        for filename in fnmatch.filter(filenames, '*.jpg'):
            if os.path.getsize(root + '/' + filename) > 20000:
                progressive = '--all-progressive'
            else:
                progressive = ''
            if quality < 100:
                quality = '-m' + str(quality)
            else:
                quality = ''
                run.local('jpegoptim ' + progressive + ' ' + quality + ' "' + root + '/' + filename + '"', ignore_exit_code = True)

@out.indent
def optimize_png():
    out.log('optimizing pngs...', 'image')
    for root, dirnames, filenames in os.walk(engine.LOCAL_WWW_DIR):
        for filename in fnmatch.filter(filenames, '*.png'):
            original_name = root + '/' + filename
            optimized_name = root + '/' + filename[:-4] + '.opt.png'
            run.local('pngcrush -q -rem alla -nofilecheck -reduce -m 7 "' + original_name + '" "' + optimized_name + '"', halt_on_stderr = False)
            if os.path.isfile(optimized_name):
                new_size = os.path.getsize(optimized_name)
                old_size = os.path.getsize(original_name)
                if new_size < old_size:
                    out.log('could reduce ' + original_name + ': ' + str(old_size) + ' --> ' + str(new_size) + ' bytes (' + str(100-100*new_size/old_size) + '%)', 'image')
                    run.local('rm "' + original_name + '"')
                    run.local('mv "' + optimized_name + '" "' + original_name + '"')
                else:
                    out.log('could not reduce ' + original_name + ': (0%).', 'image')
                    run.local('rm "' + optimized_name + '"')
            else:
                out.log('pngcrush did decide not to write an output file for ' + original_name, 'image')

