#this filw must not have any dependencies on other modules!
#only python standard modules are allowed
#import all constants
try:
    #this import will work when we are in scripts folder
    from config.config import LOG_LEVEL, LEVEL_NONE, LEVEL_ERROR, LEVEL_WARNING, LEVEL_INFO, LEVEL_VERBOSE, LEVEL_DEBUG, LOG_FILE
except ImportError:
    print "Could not import config package. Try navigating to script folder before starting the script."
    exit()

from codecs import open

last_output_blocked = False
output_blocked_from_parent = False

filter_output = ['Warning: Using a password on the command line interface can be insecure.',
                 'mysqldump: [Warning] Using a password on the command line interface can be insecure.',
                 '[Warning] Using a password on the command line interface can be insecure.',
                 'mysql: [Warning] Using a password on the command line interface can be insecure.']

#the indentation level, so you can see which function triggered what
indentation = -1

#logs a message to the screen, depending on current indentation and output level
def log(msg, domain = 'command', output_level = LEVEL_INFO):
    global current_output_level
    global indentation

    global last_output_blocked
    global output_blocked_from_parent

    msg = msg.rstrip()

    if msg in filter_output:
        return

    #handle indentation
    indentation_string = ''
    for i in range(indentation):
        indentation_string += '  '

    #assemble output
    if isinstance(msg, str):
        msg = unicode(msg, 'utf-8' )
    try:
        prefix = unicode(indentation_string) + u'[' + unicode(domain) + u'] '
        output = prefix + msg.replace('\n', '\n' + prefix)
    except:
        output = msg

    #just log everything to output file
    log_to_output_file(output)

    #the parents output did not come through, so we won't print anything
    if output_blocked_from_parent and output_level > LEVEL_WARNING:
        return

    #only output stuff that we actually want to see
    last_output_blocked = output_level > LOG_LEVEL
    if last_output_blocked:
        return

    #print output
    print output

#reads a file and logs it onto screen using log
def file(filename, domain, output_level = LEVEL_INFO):
    import os
    if not os.path.isfile(filename):
        return
    file = open(filename, "r")
    for line in file:
        log(line, domain, output_level)

#mostly used internally to handle indentation
def increase_indentation(levels = 1):
    global indentation
    indentation += levels

#used internally most of the time by the decorator
def decrease_indentation(levels = 1):
    global indentation
    indentation -= levels
    if levels < -1:
        log('Warning: Indentation is smaller than -1. Set to -1.', 'output', LEVEL_WARNING)
        indentation = -1

def log_to_output_file(output):
    if LOG_FILE is None:
        return
    file = open(LOG_FILE, 'a', encoding='utf-8')
    file.write(output + "\n")
    file.close

def clear_logfile():
    if not LOG_FILE is None:
        file = open(LOG_FILE, 'w')
        file.close()

#decorator, that will cause output of function calls of this function to be indented.
#this is also taking care of supressing output if the last output has been surpressed.
def indent(func):
    def indenting_func(*args, **kwargs):
        global output_blocked_from_parent
        global last_output_blocked

        #ok simple, increase the indentation value
        increase_indentation()

        #save these values
        restore_output_parent = output_blocked_from_parent
        restore_output_last = last_output_blocked

        #overwrite global value for next nested level
        output_blocked_from_parent = last_output_blocked or output_blocked_from_parent

        #execute original function
        result = func(*args, **kwargs)

        #restore values
        output_blocked_from_parent = restore_output_parent
        last_output_blocked = restore_output_last

        #decrease indentation
        decrease_indentation()

        #don't forget to give back result
        return result
    return indenting_func
