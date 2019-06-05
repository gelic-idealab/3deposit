# library for unpacking gateway request object
# utilities include: unpack_config, unpack_auth, unpack_data, unpack_file

import json

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], a + '_')

        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def get_value(request, scope, field):
    request_json = json.loads(request.form.get(scope))
    flat_request = flatten_json(request_json)
    return flat_request.get(field)   