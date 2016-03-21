

LEVEL_NONE = 0
LEVEL_ERROR = 1
LEVEL_WARNING = 2
LEVEL_INFO = 3
LEVEL_DEBUG = 5

current_output_level = LEVEL_DEBUG
maximum_indentation_output = -1 #set this to a negative value to output all indentation

#the indentation level, so you can see which function triggered what
indentation = 0

def log(msg, output_level = LEVEL_INFO):
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
    print str(indentation_string) + str(msg)

def increase_indentation(levels = 1):
    global indentation
    indentation += levels

def decrease_indentation(levels = 1):
    global indentation
    indentation -= levels
    if levels < 0:
        out('[output] Warning: Indentation is negative. Set to 0.')
        indentation = 0

#decorator, that will cause output of function calls of this function to be indented.
#For better understanding of the program flow and what of why happend where
def indent(func):
    def indenting_func(*args, **kwargs):
        increase_indentation()
        result = func(*args, **kwargs)
        decrease_indentation()
        return result
    return indenting_func
