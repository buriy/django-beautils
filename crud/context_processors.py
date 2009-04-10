from crud.models import get_CRUDs

def CRUD(request):
    return {'CRUD': get_CRUDs()}
