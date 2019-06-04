# library for unpacking gateway request object
# utilities include: unpack_config, unpack_auth, unpack_data, unpack_file

#auth_obj = get_value_from_request_key(request, scope='config', key='access_key')

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], a + '_')
        # elif type(x) is list:
        #     i = 0
        #     for a in x:
        #         flatten(a, name + str(i) + '_')
        #         i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def get_value(request, scope, field):
    # for key in request[scope].unpack():
    #     value = key['value']
    # return key

    request_json = json.loads(request.form.get(scope))

    flat_request = flatten_json(request_json)

    if key in flat_request:
        return flat_request.get(key)
    else:
        return {"err":"Please provide valid scope and keys."}        