from utils.commons.namedtuple import namedtuple

def qs_filter(model_or_queryset, **filters):
    if isinstance(model_or_queryset, (list, tuple)):
        if filters:
            raise Exception("Can't apply filters to a list")
        return model_or_queryset
    if hasattr(model_or_queryset, 'model'):
        qs = model_or_queryset
    else:
        qs = model_or_queryset.objects.all()
    if filters:
        return qs.filter(**filters)
    else:
        return qs

def as_list(model_or_queryset, col, **filters):
    qs = qs_filter(model_or_queryset, **filters)
    return [x[col] for x in qs.values(col)]

def as_set(model_or_queryset, col, **filters):
    return set(as_list(model_or_queryset, col, **filters))

def as_dict(model_or_queryset, col_key, col_value, **filters):
    qs = qs_filter(model_or_queryset)
    return dict([(x[col_key], x[col_value]) for x in qs.values(col_key, col_value)])

def as_map(model_or_queryset, key, **filters):
    qs = qs_filter(model_or_queryset)
    return dict([(getattr(x, key), x) for x in qs])

def as_map_tuples(model_or_queryset, key, **filters):
    """ Useful after queryset.values() """
    qs = qs_filter(model_or_queryset)
    return dict([(getattr(x, key), x) for x in as_tuples_iter(qs)])

def as_tuples(model_or_queryset, cols, **filters):
    """ Useful after queryset.values() """
    qs = qs_filter(model_or_queryset)
    Row = namedtuple('Row', cols)
    return [Row(*[row[key] for key in cols]) for row in qs]

def as_tuples_iter(model_or_queryset, cols, **filters):
    """ Useful after queryset.values() """
    qs = qs_filter(model_or_queryset, **filters)
    Row = namedtuple('Row', cols)
    for row in qs:
        yield Row(*[row[key] for key in cols])
