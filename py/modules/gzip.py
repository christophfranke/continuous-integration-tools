#this module takes care of compression using the tar command
import engine
import out
import run


#compress a single file
@out.indent
def compress(uncompressed_file, run_func, rename_tmp_func = None):
    #this will be the name of the compressed file
    compressed_file = uncompressed_file + '.gz'

    #tell user
    out.log('compressing ' + uncompressed_file, 'zip', out.LEVEL_VERBOSE)

    #tell engine that we moved a file
    if rename_tmp_func is not None:
        rename_tmp_func(uncompressed_file, compressed_file)

    #compress
    run_func('gzip ' + uncompressed_file)

    #return file
    return compressed_file

#uncompress a single file
@out.indent
def uncompress(compressed_file, run_func, rename_tmp_func = None):
    #tell user
    out.log('uncompressing ' + compressed_file, 'zip', out.LEVEL_VERBOSE)
    if compressed_file[-3:] != '.gz':
        out.log('Error: Compressed file does not have the .gz suffix. Something is going wrong here.', 'zip', out.LEVEL_ERROR)
        exit()

    #uncompressed file is compressed file without the last three characters
    uncompressed_file = compressed_file[:-3]

    #tell engine
    if rename_tmp_func is not None:
        rename_tmp_func(compressed_file, uncompressed_file)

    #uncompress
    run_func('gzip --uncompress ' + compressed_file)

    #return file
    return uncompressed_file


def compress_local(filename, tell_engine = False):
    if tell_engine:
        rename_tmp_func = engine.rename_local_file
    else:
        rename_tmp_func = None
    return compress(filename, run.local, rename_tmp_func)

def uncompress_local(filename, tell_engine = False):
    if tell_engine:
        rename_tmp_func = engine.rename_local_file
    else:
        rename_tmp_func = None
    return uncompress(filename, run.local, rename_tmp_func)

def compress_remote(filename, tell_engine = False):
    if tell_engine:
        rename_tmp_func = engine.rename_remote_file
    else:
        rename_tmp_func = None
    return compress(filename, run.remote, rename_tmp_func)

def uncompress_remote(filename, tell_engine = False):
    if tell_engine:
        rename_tmp_func = engine.rename_remote_file
    else:
        rename_tmp_func = None
    return uncompress(filename, run.remote, rename_tmp_func)

#decide if that file is compressed. Note that it does not actually read the file but decides this only by filename
def is_compressed(filename):
    return filename[-3:] == '.gz'

def compressed_filename(filename):
    #no file, nothing to do
    if filename is None:
        return None
    #is already compressed, nothing to do
    if is_compressed(filename):
        return filename
    #append .gz
    return filelname + '.gz'

def uncompressed_filename(filename):
    #no file, nothing to do
    if filename is None:
        return None
    #is not compressed, nothing to do
    if not is_compressed(filename):
        return filename
    #remove last three characters
    return filename[:-3]
