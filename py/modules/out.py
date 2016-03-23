#this filw must not have any dependencies on other modules!
#only python standard modules are allowed
#import all constants
try:
    #this import will work when we are in scripts folder
    from config.config import LOG_LEVEL, LEVEL_NONE, LEVEL_ERROR, LEVEL_WARNING, LEVEL_INFO, LEVEL_VERBOSE, LEVEL_DEBUG
except ImportError:
    try:
        #this will work form other places (relative import)
        from ...config.config import LOG_LEVEL, LEVEL_NONE, LEVEL_ERROR, LEVEL_WARNING, LEVEL_INFO, LEVEL_VERBOSE, LEVEL_DEBUG
    except ImportError:
        #we are out of luck...
        print "Could not import config package. Try navigating to script folder before starting the script."
        exit()


last_output_blocked = False
output_blocked_from_parent = False

#the indentation level, so you can see which function triggered what
indentation = -1

#logs a message to the screen, depending on current indentation and output level
def log(msg, domain = 'command', output_level = LEVEL_INFO):
    global current_output_level
    global indentation

    global last_output_blocked
    global output_blocked_from_parent

    #the parents output did not come through, so we shouldn't go into further detail here
    if output_blocked_from_parent and output_level > LEVEL_WARNING:
        return

    #only output stuff that we actually want to see
    last_output_blocked = output_level > LOG_LEVEL
    if last_output_blocked:
        return

    #handle indentation
    indentation_string = ''
    for i in range(indentation):
        indentation_string += '  '

    #print!
    print str(indentation_string) + '[' + str(domain) + '] ' + str(msg)

#reads a file and logs it onto screen using log
def file(filename, domain,output_level = LEVEL_INFO):
    import os
    if not os.path.isfile(filename):
        return
    file = open(filename, "r")
    for line in file:
        log(line.rstrip(), domain, output_level)

#mostly used internally to handle indentation
def increase_indentation(levels = 1):
    global indentation
    indentation += levels

#used internally most of the time by the decorator
def decrease_indentation(levels = 1):
    global indentation
    indentation -= levels
    if levels < -1:
        log('[output] Warning: Indentation is smaller than -1. Set to -1.')
        indentation = -1


#decorator, that will cause output of function calls of this function to be indented.
#For better understanding of the commands flow and what of why happend where
def indent(func):
    def indenting_func(*args, **kwargs):
        global output_blocked_from_parent
        global last_output_blocked
        increase_indentation()
        restore_output_parent = output_blocked_from_parent
        restore_output_last = last_output_blocked
        output_blocked_from_parent = last_output_blocked or output_blocked_from_parent
        result = func(*args, **kwargs)
        output_blocked_from_parent = restore_output_parent
        last_output_blocked = restore_output_last
        decrease_indentation()
        return result
    return indenting_func
