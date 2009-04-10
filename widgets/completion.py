def to_autocomplete_string(results):
    if results:
        for result in results:
            yield '%s|%s\n' % (result.name, result.pk)
