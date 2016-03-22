#this fiel must not have any dependencies!

LEVEL_NONE = 0
LEVEL_ERROR = 1
LEVEL_WARNING = 2
LEVEL_INFO = 3
LEVEL_DEBUG = 5

current_output_level = LEVEL_INFO
maximum_indentation_output = -1 #set this to a negative value to output all indentation

#the indentation level, so you can see which function triggered what
indentation = 0

#logs a message to the screen, depending on current indentation and output level
def log(msg, domain = 'command', output_level = LEVEL_INFO):
    global current_output_level
    global indentation

    #only output stuff that we actually want to see
    if output_level < current_output_level and (maximum_indentation_output >= 0 or indentation <= maximum_indentation_output):
        return

    #handle indentation
    indentation_string = ''
    for i in range(indentation):
        indentation_string += '  '

    #print!
    print str(indentation_string) + '[' + str(domain) + '] ' + str(msg)

#reads a file and logs it onto screen using log
def file(filename, domain,output_level = LEVEL_INFO):
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
    if levels < 0:
        log('[output] Warning: Indentation is negative. Set to 0.')
        indentation = 0


#decorator, that will cause output of function calls of this function to be indented.
#For better understanding of the commands flow and what of why happend where
def indent(func):
    def indenting_func(*args, **kwargs):
        increase_indentation()
        result = func(*args, **kwargs)
        decrease_indentation()
        return result
    return indenting_func
