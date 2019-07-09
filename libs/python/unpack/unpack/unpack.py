# library for unpacking 3deposit gateway request object
import json

def _flatten_json(y):
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
    if request.form:
        request_json = json.loads(request.form.get(scope))
    elif request.json:
        request_json = request.json
    else:
        return None
    flat_request = _flatten_json(request_json)
    return flat_request.get(field)
