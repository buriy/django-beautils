def get_queryset(model_or_queryset):
    if hasattr(model_or_queryset, 'model'):
        return model_or_queryset

def as_list(model_or_queryset, col):
    qs = get_queryset(model_or_queryset)
    return [x[col] for x in qs.values(col)]

def as_set(model, col):
    return set(as_list(model, col))

def as_dict(model_or_queryset, col_key, col_value):
    qs = get_queryset(model_or_queryset)
    return dict([(x[col_key], x[col_value]) for x in qs.values(col_key, col_value)])
