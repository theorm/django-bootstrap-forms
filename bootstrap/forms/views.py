from django.shortcuts import render_to_response
from django.template.context import RequestContext
from forms import BootstrapFormMixin,Field,Inline,Addon,TEMPLATE_PREFIX
from django import forms


class ExampleForm(BootstrapFormMixin,forms.Form):
    class Meta:
        bootstrap = (
            Field('first_name',span=5),
            Inline('Stay',(Field('arrival',span=2),'to',Field('departure',span=2))),
            Addon(field=Field('rate',span=1),addon='$',prepend=False),
            Addon(field=Field('gst',span=1),addon=Field('add_gst')),
        )

    first_name = forms.CharField(help_text='E.g. John')
    last_name = forms.CharField(help_text='E.g. Doe')
    rate = forms.IntegerField(help_text='AUD')
    gst = forms.IntegerField(help_text='%',label='GST')
    add_gst = forms.BooleanField()
    arrival = forms.DateField(help_text='How long')
    departure = forms.DateField(help_text='to stay?')
    secret_field = forms.CharField(widget=forms.HiddenInput,required=True)

def example_form(request):
    form = ExampleForm()
    error_form = ExampleForm({'rate' : 'asdf','add_gst' : 'true'})
    error_form.is_valid()
    return render_to_response(TEMPLATE_PREFIX % 'example_form.html', {'form' : form, 'error_form' : error_form}, RequestContext(request))
