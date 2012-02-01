from django.template.loader import get_template
from bootstrap.forms.forms import TEMPLATE_PREFIX, _bound_field_context, Field,\
    _merge_field
from django.forms.forms import BoundField
from django.template.context import Context
from django.template import Library, Node, TemplateSyntaxError 
from django.template.defaulttags import kwarg_re
from django.conf import settings

register = Library()

class BootstrapFieldNode(Node):
    def __init__(self,args,kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def render(self,ctx):
        attrs = {}
        
        if hasattr(settings,'BOOTSTRAP_HELP_BLOCK') and settings.BOOTSTRAP_HELP_BLOCK:
            help_inline = False
        else:
            help_inline = True
            
        if 'hide' in self.kwargs:
            hide_field = bool(self.kwargs['hide'])
        else:
            hide_field = False
        
        if 'span' in self.kwargs:
            attrs['class'] = Field.SPAN % self.kwargs['span'].resolve(ctx)
            
        if 'label' in self.kwargs:
            label = self.kwargs['label'].resolve(ctx)
        else:
            label = None
            
        if 'required' in self.kwargs:
            required=True
        else:
            required=False
        
        if 'after' in self.kwargs:
            after = self.kwargs['after'].resolve(ctx)
        else:
            after = None
            
        if len(self.args) > 1:
            template = get_template(TEMPLATE_PREFIX % "inline_field.html")
            contexts = tuple()
            for field in [f.resolve(ctx) for f in self.args]:
                if isinstance(field,BoundField):
                    contexts = contexts + (_bound_field_context(field,widget_attrs=attrs.copy()),)
                else:
                    contexts = contexts + (field,)
                                    
            help = _merge_field(contexts,'help_text')
            errors = _merge_field(contexts,'errors')
            
            return template.render(Context({
                    'fields' : contexts, 
                    'label' : label, 
                    'help' : help, 
                    'errors' : errors, 
                    'help_inline': help_inline, 
                    'hide': hide_field, 
                    'required' : required,
                    'after' : after
            }))
    
        else:
            if 'prepend' in self.kwargs or 'append' in self.kwargs:
                if 'prepend' in self.kwargs:
                    template = get_template(TEMPLATE_PREFIX % "addon_field_prepend.html")
                else:
                    template = get_template(TEMPLATE_PREFIX % "addon_field_append.html")
                
                addon = self.kwargs.get('prepend',self.kwargs.get('append')) 
                addon = addon.resolve(ctx)

                context = {'help_inline': help_inline, 'hide': hide_field, 'after' : after}
                
                context['field'] = _bound_field_context(self.args[0].resolve(ctx),widget_attrs=attrs.copy())
                context['required'] = self.args[0].resolve(ctx).field.required
                if isinstance(addon,BoundField):
                    context['addon'] =  _bound_field_context(addon)
                else:
                    context['addon'] = addon
                
                context['help'] = _merge_field([context['field'],context['addon']],'help_text')
                context['errors'] = _merge_field([context['field'],context['addon']],'errors')
                
                return template.render(Context(context))
            else:
                template = get_template(TEMPLATE_PREFIX % "field.html")
                context = _bound_field_context(self.args[0].resolve(ctx),widget_attrs=attrs.copy())
                context['required'] = self.args[0].resolve(ctx).field.required
                context['help_inline'] = help_inline
                context['hide'] = hide_field
                context['after'] = after
                return template.render(Context(context))

@register.tag
def bootstrap_field(parser,token):
    
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument - a field" % bits[0])
    args = []
    kwargs = {}
    bits = bits[1:]
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))
    
    if not len(args):
        return ''

    return BootstrapFieldNode(args,kwargs)
