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
    

class ProtocolFilterForm(forms.Form):
    baustelle = forms.CharField(max_length=100, required=False, label='Baustelle')
    fahrzeug = forms.CharField(max_length=100, required=False, label='Fahrzeug')
    protocol_name = forms.CharField(max_length=100, required=False, label='Protocol Type')
    teil = forms.ChoiceField(
        choices=[('all', 'All'), 
                 ("hubzug", "Hubzug")],
        required=False,
        label='Teil'
    )
    status = forms.ChoiceField(
        choices=[('all', 'All'), 
                 ("offen", "Offen"),
                 ('exported', 'Abgeschlossen'), 
                 ('closed', 'Zur Überprüfung'), 
                 ('saved', 'In Bearbeitung'),
                 ('correction', 'Korrektur erforderlich')],
        required=False,
        label='Status'
    )