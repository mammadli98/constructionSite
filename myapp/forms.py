from django import forms
from .models import *

class NewBaustelleForm(forms.ModelForm):
    class Meta:
        model = newBaustelle
        fields = ['baustelleName']

class NewFahrzeugForm(forms.ModelForm):
    class Meta:
        model = newFahrzeug
        fields = ['fahrzeugName', 'isVisible', 'baustelle']