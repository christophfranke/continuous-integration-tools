import out

#decorator for buffering calls such as ftp
def buffered(func):

    #turn off buffering by default
    func.buffering_on = False
    func.delimiter = '\n'
    func.buffer = '';
    func.name = str(func)

    #buffers when buffering is enabled
    def buffered_func(buffered_input, *args, **kwargs):
        if func.buffering_on:
            out.log('buffering call for ' + buffered_input, func.name, out.LEVEL_DEBUG)
            func.buffer += buffered_input + func.delimiter
        else:
            out.log('executing unbuffered call ' + buffered_input, func.name, out.LEVEL_DEBUG)
            func(buffered_input, *args, **kwargs)

    #flush the buffer
    def flush(*args, **kwargs):
        if len(func.buffer) > 0:
            out.log('executing flush ' + func.buffer, func.name, out.LEVEL_DEBUG)
            func(func.buffer, *args, **kwargs)
            func.buffer = ''

    #start buffering
    def start():
        out.log('start buffering', func.name, out.LEVEL_DEBUG)        
        func.buffering_on = True

    def end():
        out.log('stop buffering', func.name, out.LEVEL_DEBUG)
        flush()
        func.buffering_on = False

    def name(name):
        func.name = 'buffered ' + name

    buffered_func.set_name = name
    buffered_func.start_buffer = start
    buffered_func.flush_buffer = flush
    buffered_func.end_buffer = end

    return buffered_func
