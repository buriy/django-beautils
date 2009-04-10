#it's important to extend from this mixin class
class AltersGlobals(object):
    def set_global(self, context, name, value):
        globalDict = get_global_dict(context)
        globalDict[name] = value
        context[name] = value

class GlobalDict(dict):
    pass

def get_global_dict(context):
    if len(context.dicts)>0 and type(context.dicts[-1]) is GlobalDict:
        return context.dicts[-1]
    else:
        globalDict = GlobalDict()
        context.dicts.append(globalDict)
        return globalDict

def set_global(context, name, value):
    globalDict = get_global_dict(context)
    globalDict[name] = value
    context[name] = value

