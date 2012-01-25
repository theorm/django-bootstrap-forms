from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from django.template.context import Context
from django import forms
from django.conf import settings

TEMPLATE_PREFIX='bootstrap/forms/%s'

if hasattr(settings,'BOOTSTRAP_HELP_BLOCK') and settings.BOOTSTRAP_HELP_BLOCK:
    help_inline = False
else:
    help_inline = True


def _merge_field(collections,key):
    'Merge lists from collection[key] in every collection, remove duplicates and empty strings'
    result = []
    for collection in collections:
        if isinstance(collection,dict):
            value = collection.get(key,[])
            if isinstance(value,list):
                result.extend(value)
            else:
                result.append(value)
    result = [i for i in set(result) if i.strip() != '']
    return result

def _bound_field_context(bf,form=None,widget_attrs={}):
        if bf.label:
            label = conditional_escape(force_unicode(bf.label))
            # Only add the suffix if the label does not end in
            # punctuation.
            if form and form.label_suffix:
                if label[-1] not in ':?.!':
                    label += form.label_suffix
            else:
                label += ':'
            label = bf.label_tag(label) or ''
        else:
            label = ''
        
        if bf.field.help_text:
            help_text = force_unicode(bf.field.help_text)
        else:
            help_text = u''
            
        return {
            'errors' : bf.errors,
            'label' : mark_safe(label),
            'field' : bf.as_widget(attrs=widget_attrs),
            'help_text' : help_text,
            'help_inline' : help_inline,
            'required' : bf.field.required
        }

class BaseField(object):
    class Meta:
        abstract = True
        
    def render(self,form,fields):
        context = self.get_context(form,fields)
        template = self.get_template()
        return template.render(Context(context))

    def get_context(self,form,fields):
        raise NotImplementedError()
        
    def get_template(self):
        raise NotImplementedError()

class Field(BaseField):
    SPAN = 'span%s'
    
    def __init__(self,field,span=None):
        self.field_name = field
        self.span=span is not None and int(span) or None
        
    def get_context(self,form,fields):
        bf = fields.pop(self.field_name)
        attrs = {}
        if self.span:
            attrs['class'] = self.SPAN % self.span

        return _bound_field_context(bf,form,attrs)
    
    def get_template(self):
        return get_template(TEMPLATE_PREFIX % "field.html")

class Inline(BaseField):
    def __init__(self,label=None,fields=[]):
        self.inline_fields = fields
        self.label = label

    def get_template(self):
        return get_template(TEMPLATE_PREFIX % "inline_field.html")
        
    def render(self,form,fields):
        contexts = tuple()
        for inline_field in self.inline_fields:
            if isinstance(inline_field,BaseField):
                contexts = contexts + (inline_field.get_context(form,fields),)
            else:
                contexts = contexts + (inline_field,)
                
        help = _merge_field(contexts,'help_text')
        errors = _merge_field(contexts,'errors')

        template = self.get_template()
        return template.render(Context({'fields' : contexts, 'label' : self.label, 'help' : help, 'errors' : errors, 'help_inline' : help_inline}))

class Addon(BaseField):
    def __init__(self,field,addon,prepend=True):
        self.field = field
        self.addon = addon
        self.prepend = prepend
        
    def get_template(self):
        if self.prepend:
            return get_template(TEMPLATE_PREFIX % "addon_field_prepend.html")
        else:
            return get_template(TEMPLATE_PREFIX % "addon_field_append.html")
        
    def render(self,form,fields):
        context = {'help_inline' : help_inline}

        context['field'] = self.field.get_context(form,fields)
                
        if isinstance(self.addon,BaseField):
            context['addon'] = self.addon.get_context(form,fields)
        else:
            context['addon'] = self.addon
        
        context['help'] = _merge_field([context['field'],context['addon']],'help_text')
        context['errors'] = _merge_field([context['field'],context['addon']],'errors')
        
        return self.get_template().render(Context(context))
        
class BootstrapFormMixin(object):
    
    def _bootstrap_fields(self):
        if hasattr(self,'Meta') and hasattr(self.Meta,'bootstrap'):
            return self.Meta.bootstrap
        return  []
    
    def bootstrap_fields(self):
        'Get bootstrap _visible only_ fields as rendered html'         
        fields = {}
        for f in self.visible_fields():
            fields[f.name] = f
            
        for bootstrap_field in self._bootstrap_fields():
            yield bootstrap_field.render(self,fields)

        for field in fields.copy():
            yield Field(field).render(self,fields)
        
    
    def as_div(self):
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []

        for field in self.hidden_fields():
            if field.errors:
                top_errors.extend(['%s: %s' % (field.label,e) for e in field.errors])
            hidden_fields.append(unicode(field))
                
        for snippet in self.bootstrap_fields():
            output.append(snippet)
        
        if top_errors:
            output.insert(0,self.get_top_error_template().render(Context({'errors' : top_errors})))
            
        if hidden_fields:
            output.extend(hidden_fields)
            
        return mark_safe('\n'.join(output))
        
    def get_top_error_template(self):
        return get_template(TEMPLATE_PREFIX % 'top_errors.html')

    def __unicode__(self):
        return self.as_div()
    
    
class Form(BootstrapFormMixin,forms.Form):
    pass

class ModelForm(BootstrapFormMixin,forms.ModelForm):
    pass
