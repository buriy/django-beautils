from lang.namedtuple import namedtuple
from lang.func import select_keys

def qs_filter(morqs, **filters):
    """
    morqs = model or queryset
    """
    if isinstance(morqs, (list, tuple)):
        if filters:
            raise Exception("Can't apply filters to a list")
        return morqs
    if hasattr(morqs, 'model'):
        qs = morqs
    else:
        #TODO: change to objects.get_queryset() ?
        qs = morqs.objects.all()
    if filters:
        return qs.filter(**filters)
    else:
        return qs

### QuerySet utility functions
def as_list(qs, col):
    return [x[col] for x in qs.values(col)]

def as_set(qs, col):
    return set(as_list(qs, col))

def in_bulk(qs):
    return as_set(qs, 'id')

def as_dict(qs, col_key, col_value):
    return dict([(x[col_key], x[col_value]) for x in qs.values(col_key, col_value)])

def as_map(qs, key):
    return dict([(getattr(x, key), x) for x in qs])

def as_tuplemap(qs, keys):
    return dict([(select_keys(x.__dict__, keys), x) for x in qs])

### ValueQuerySet utility functions
def as_map_tuples(vqs, key):
    """ Useful after queryset.values() """
    return dict([(getattr(x, key), x) for x in as_tuples_iter(vqs)])

def as_tuples(vqs, cols):
    """ Useful after queryset.values() """
    Row = namedtuple('Row', cols)
    return [Row(*[row[key] for key in cols]) for row in vqs]

def as_tuples_iter(vqs, cols):
    """ Useful after queryset.values() """
    Row = namedtuple('Row', cols)
    for row in vqs:
        yield Row(*[row[key] for key in cols])
