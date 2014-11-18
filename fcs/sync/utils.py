def update_obj(obj, d):
    if not d:
        obj = None
    else:
        for name, value in d.iteritems():
            setattr(obj, name, value)
    return obj
