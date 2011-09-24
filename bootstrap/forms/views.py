from django.shortcuts import render_to_response
from django.template.context import RequestContext
from forms import BootstrapFormMixin,Field,Inline,Addon,TEMPLATE_PREFIX
from django import forms


class ExampleForm(BootstrapFormMixin,forms.Form):
    class Meta:
        bootstrap = (
            Field('flight',span=3),
            Inline('Flying',('from', Field('ex',span=2),'to',Field('to',span=2))),
            Addon(field=Field('price',span=1),addon='$',prepend=False),
            Addon(field=Field('gst',span=1),addon=Field('add_gst')),
        )

    flight = forms.CharField(help_text='E.g. CA147')
    ex = forms.CharField(help_text='E.g. Shanghai')
    to = forms.IntegerField(help_text='E.g. Sydney')
    price = forms.IntegerField(help_text='AUD',label='GST')
    gst = forms.IntegerField(help_text='%',label='GST')
    add_gst = forms.BooleanField()
    secret_field = forms.CharField(widget=forms.HiddenInput,required=True)


def example_form(request):
    form = ExampleForm()
    error_form = ExampleForm({'price' : 'asdf','add_gst' : 'true'})
    error_form.is_valid()
    return render_to_response(TEMPLATE_PREFIX % 'example_form.html', {'form' : form, 'error_form' : error_form}, RequestContext(request))
