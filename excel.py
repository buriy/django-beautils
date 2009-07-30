from utils.queries import get_queryset
from utils.commons.func import seq_uniq
from utils.commons.strings import force_quote, quote
from utils.commons.skipper import SkipLine, SkipFile
import csv

DATE_FORMATS = ['%d-%b-%y', '%m/%d/%y', '%m/%d/%Y', '%d %B %Y']

def parse_excel_date(d, formats = DATE_FORMATS):
    import datetime
    import time
    d = d.strip()
    exception = None
    for format in formats:
        try:
            #return datetime.datetime.strptime(d, format).date()
            return datetime.date(*(time.strptime(d, format)[0:3]))
        except ValueError, e:
            exception = e
    if exception:
        #show only exception about last format parse failed
        raise exception

def format_excel_date(d):
    return d.strptime('%Y-%m-%d') # ISO

def import_csv(fn, morqs, keys, strings={}, dates={}, overrides={}, post_process=None, verbose=True, save=True):
    added = []
    qs = get_queryset(morqs)
    M = qs.model
    for row in csv.DictReader(open(fn, 'r')):
        data_key = [(k, v) for k,v in strings.items() if v in keys]
        try:
            if not qs.filter(**keys).count():
                raise SkipLine() # ability to short-circuit skip row
            e = M()
            for k, v in strings.items():
                setattr(e, v, row[k].decode('latin1'))
            for k, v in dates.items():
                setattr(e, v, parse_excel_date(row[k]))
            for k, func in overrides.items():
                value = func
                if callable(func):
                    value = func(e, k)
                setattr(e, k, value)
            if post_process:
                post_process(e)
            if save:
                e.save()
            added.append(e)
            if verbose: print "Saved", repr(data_key)
        except SkipLine, e:
            if verbose: print "Skipped", repr(data_key)
            continue
        except SkipFile, e:
            if verbose: print "Terminated by", repr(data_key)
            break
    return added

def export_csv(stream, morqs, strings, dates={}, overrides={}):
    w = csv.writer(stream)
    qs = get_queryset(morqs)
    field_names = seq_uniq(strings.keys() + dates.keys() + overrides.keys())
    w.write(map(force_quote, field_names))
    for row in qs:
        try:
            d = {}
            for k,v in strings.items():
                item = row[k].unicode(v).encode('utf-8')
                d[k] = quote(item)
            for k,v in dates.items():
                d[k] = format_excel_date(row[k])
            for k, func in overrides.items():
                value = func
                if callable(func):
                    value = func(d, row[k])
                d[k] = value
            w.write([d[k] for k in field_names])
        except SkipLine:
            continue
        except SkipFile:
            break
    return w

def sample_usage():
    strings = {
        'Contact details': 'contact',
        'Description': 'description',
        'Event Name': 'name',
        'Event Type': 'event_type',
        'Event Organiser': 'organizer',
        'Link URL': 'link_url',
        'Location': 'location',
        'Notes': 'notes'
    }
    
    dates = {
        'End Date': 'end_date',
        'Start Date': 'start_date',
    }
    
    from apps.places.models import Event #@UnresolvedImport
    
    #fn = 'Offshore Events_WN_CSV.csv'
    #items = import_csv(fn, Event, 'name', strings, dates, save=False)
    #print "Imported %s items." % len(items)
    export_csv(open('Offshort Events New.csv', 'w'), Event, strings, dates)

if __name__ == '__main__':
    sample_usage()