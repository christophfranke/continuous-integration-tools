import out

#decorator for buffering calls such as ftp
def buffered(func):

    #turn off buffering by default
    func.buffering_on = False
    func.delimiter = '\n'
    func.buffer = '';
    func.name = str(func)

    #buffers when buffering is enabled
    @out.indent
    def buffered_func(buffered_input, *args, **kwargs):
        if func.buffering_on:
            out.log('buffering ' + buffered_input, func.name, out.LEVEL_DEBUG)
            func.buffer += buffered_input + func.delimiter
        else:
            func(buffered_input, *args, **kwargs)

    #flush the buffer
    @out.indent
    def flush(*args, **kwargs):
        if len(func.buffer) > 0:
            out.log('executing buffer', func.name, out.LEVEL_DEBUG)
            func(func.buffer, *args, **kwargs)
            func.buffer = ''

    #start buffering
    @out.indent
    def start():
        if not func.buffering_on:
            out.log('start buffer', func.name, out.LEVEL_DEBUG)        
            func.buffering_on = True

    @out.indent
    def end():
        out.log('end buffer', func.name, out.LEVEL_DEBUG)
        flush()
        func.buffering_on = False

    def name(name):
        func.name = name + '*'

    def non_empty():
        return len(func.buffer) > 0

    buffered_func.set_name = name
    buffered_func.start_buffer = start
    buffered_func.flush_buffer = flush
    buffered_func.end_buffer = end
    buffered_func.has_buffer = non_empty

    return buffered_func
