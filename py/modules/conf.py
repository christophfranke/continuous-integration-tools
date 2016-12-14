import out


#filter constant names: valid constant names contain of only uppercase letters and underscores
def valid_constant(const_name):
    if re.match('(_|[A-Z])+$', const_name):
        return True
    else:
        return False

def add_config(key, value, type='string'):
    import out

    if not valid_constant(key):
        log.out('Not a valid configuration name: ' + key, 'engine', out.LEVEL_ERROR)
        quit()

    if type == 'string':
        escaped_value = "'" + str(value) + "'"
    else:
        escaped_value = str(value)

    assignement = str(key) + " = " + str(escaped_value)

    #write to project config
    filename = PROJECT_CONFIG_FILE
    out.log('PROJECT_CONFIG_FILE is at ' + PROJECT_CONFIG_FILE, 'engine', out.LEVEL_DEBUG)
    file = open(filename, 'a')
    file.write("\n" + assignement + " #added automatically on " + str(datetime.now()) + "\n")
    file.close()

    #make accessible immediately
    globals()[key] = value #TODO: This probably doesn't work
    out.log("added " + assignement + " to config", 'engine', out.LEVEL_DEBUG)

#gets a config var 'key', or a dictionary of all config vars if key is not specified.
def get_config(key = None):
    if key is not None:
        if valid_constant(key):
            try:
                value = globals()[key]
                return value
            except KeyError:
                out.log('There is no constant by the name ' + key, 'engine', out.LEVEL_WARNING)
                return None
        else:
            out.log('Not a valid constant name: ' + key, 'engine', out.LEVEL_WARNING)
            return None
    else:
        config_vars = {}
        for k in globals():
            if valid_constant(k):
                config_vars[k] = globals()[k]
        return config_vars

