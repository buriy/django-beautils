from django.conf import settings
import os

DIRS = set()

GEN = settings.ROOT+'/generated/'

def ensure_dir_exists(dir):
    if not dir in DIRS:
        if not os.path.exists(dir):
            try:
                os.makedirs(dir, 0770)
            except:
                pass
        DIRS.add(dir)

def build_filename(group, name):
    name = name.replace('\\','_').replace('-','_').replace(' ','_')
    path = group + '/' + name + '.html'
    dir = os.path.dirname(path)
    ensure_dir_exists(GEN+dir)
    return path

def save_file(path, source):
    f = open(path, 'wt')
    f.write(source)
    f.close()
    
def load_file(path):
    f = open(path, 'rt')
    result = f.read()
    f.close()
    return result