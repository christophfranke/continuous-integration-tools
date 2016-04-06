import json
import hashlib
import os
import sys


def md5sum(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def save_md5_table(md5_table, filename):
    md5_table_file = open(filename, 'w')
    json.dump(md5_table, md5_table_file)
    md5_table_file.close()


def create_md5_table(root_dirname):
    root_dir = os.path.abspath(root_dirname)
    files = []
    md5_table = {}
    for root, dirnames, filenames in os.walk(root_dir):
        #for filename in fnmatch.filter(filenames, '*'):
        for filename in filenames:
            abs_file = os.path.join(root, filename)
            rel_file = abs_file[len(root_dir)+1:]
            files.append(rel_file)

    for f in files:
        try:
            md5_table[f] = md5sum(os.path.join(root_dirname,f))
        except:
            pass

    return md5_table


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Error: First argument needs to be the root folder, second argument needs to be the table file."
        exit()
    else:
        root_dir = os.path.abspath(sys.argv[1])
        table_file = os.path.abspath(sys.argv[2])
        table = create_md5_table(root_dir)
        save_md5_table(table, table_file)
        print "Done."