from django.forms.models import ModelForm, ModelFormMetaclass
from django.db.models.fields.related import ForeignKey
from django import forms
from formwidgets.jquery.widgets.datepicker import DatePickerWidget
from formwidgets.jquery.widgets.autocomplete import AutocompleteWidget

class CRUDFormBase(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback',
                lambda f: f.formfield())
        if 'CRUD' in attrs:
            autocomplete_fields = getattr(attrs['CRUD'], 'autocomplete', [])
            def autocomplete_fix(db_field, **kwargs):
                if db_field.name in autocomplete_fields:
                    kwargs['max_length'] = 128
                    kwargs['required'] = not db_field.blank
                    return forms.CharField(**kwargs)
                else:
                    return formfield_callback(db_field, **kwargs)
            attrs['formfield_callback'] = autocomplete_fix
        return super(CRUDFormBase, cls).__new__(cls, name, bases, attrs)

class CRUDForm(ModelForm):
    __metaclass__ = CRUDFormBase
    """
    Sample usage:
    
    class CombinedTeamViews(CRUDForm):
        class CRUD:
            INDEX = 'clubs_combined'
        class Meta:
            model = CombinedTeam
    
    registerCRUD(group='Clubs', path='clubs', cls=ClubForm)
    registerCRUD(group='Clubs', path='clubs/types', cls=ClubTypeForm)
    """
    
    cache = {} 
    rels = {}
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, instance=None, *args, **kwargs):
        super(CRUDForm, self).__init__(data, files, auto_id, prefix, instance=instance, *args, **kwargs)

        #autocomplete_fields = getattr(self._crud, 'autocomplete', [])

        for f in self._meta.model._meta.fields: #model fields
            if isinstance(f, ForeignKey) and not f.rel.parent_link:
                self.cache[f.name] = None
                self.rels[f.name] = f.rel.to

        self.set_widgets()
        
        for field in self:
            field.field.widget.attrs['tabindex'] = self.tabindex()
            
    def set_widgets(self):
        autocomplete_related = [] 
        autocomplete_fields = getattr(self._crud, 'autocomplete', [])
        for field in self: # field = BoundField
            if isinstance(field.field, forms.DateField):
                field.field.widget = DatePickerWidget()
            if isinstance(field.field, forms.CharField):
                if not field.name in autocomplete_fields: 
                    continue # not an autocomplete field
                classes = 'autocomplete' 
                if field.field.required:
                    classes = classes + ' required'
                field.field.widget = AutocompleteWidget(
                    attrs={'class': classes, 'size': 60},
                    choices_url='autocomplete_'+field.name,
                    related_fields=tuple(autocomplete_related),
                    options={'minChars': 0, 'maxChars': 128, 'autoFill': True, 
                             'scroll': True, 'scrollHeight': 300},
                    )
                #print self.instance.__dict__
                if getattr(self.instance, field.name+'_id', None):
                    field.field.widget.choice = getattr(self.instance, field.name)
                #prev = autocomplete_related and autocomplete_related[0]
                #fname = field.name
                #def clean_xxx():
                #    return self.cleaner(fname, prev, self.rels[fname])
                #setattr(self, 'clean_'+field.name, clean_xxx) 
                #autocomplete_related.append(field.name)

    def clean(self):
        autocomplete_related = [] 
        autocomplete_fields = getattr(self._crud, 'autocomplete', [])
        for field in self:
            if isinstance(field.field, forms.CharField):
                if not field.name in autocomplete_fields: 
                    continue # not an autocomplete field
                prev = autocomplete_related and autocomplete_related[0]
                fname = field.name
                self.cleaner(fname, prev, self.rels[fname])
        return self.cleaned_data

    def first_field(self):
        for field in self:
            return field

    def tabindex(self):
        if not hasattr(self, '_tabindex'):
            setattr(self, '_tabindex', 0)

        self._tabindex += 1
        return self._tabindex

    def cleaner(self, field, filter, Model, alt='name'):
        #print 'cleaning', field, self.cleaned_data.get(field, None) 
        value = self.cleaned_data[field]
        rel = None 
        if filter:
            rel = self.cache.get(filter, None)

        self.cache[field] = None

        if not value or (filter and not rel):
            return value

        q = {alt: value}
        if filter:
            q[filter] = rel
        
        d_list = list(Model.objects.filter(**q)[:1])
        if d_list:
            d = d_list[0]
        else:
            #FIXME: it doesn't work for Cities
            d = Model.objects.create(**q)
        
        self.cache[field] = d
        return value

    def update_images(self, imageset, image, ImageModel):
        if isinstance(image, ImageModel):
            imageset.add(image)
        elif isinstance(image, (list, tuple)):
            for i in image:
                imageset.add(ImageModel.objects.get(pk=i))
            pks = [c.pk for c in imageset.all ()]
            for pk in pks:
                if not pk in image:
                    imageset.remove(pk)

    def save(self, commit=True):
        #FIXME: super.save wants real instances in cleaned_data
        if self.is_valid():
            for f in self._meta.model._meta.fields:
                if f.name in self.cache:
                    cached = self.cache[f.name]
                    self.cleaned_data[f.name] = cached
        instance = super(CRUDForm, self).save(commit=commit)
        return instance
