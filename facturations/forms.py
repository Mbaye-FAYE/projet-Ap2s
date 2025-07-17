from django import forms
from django.forms import inlineformset_factory
from .models import Facture, Article, Client
from django import forms
class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['numero', 'numero_commande','date_emission', 'livraison']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_commande': forms.TextInput(attrs={'class': 'form-control'}),
            'date_emission': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'livraison': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['code_client','nom', 'email', 'telephone', 'adresse']
        widgets = {
            'code_client': forms.TextInput(attrs={'class': 'form-control'}),  # Champ 'code_client' avec style
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['designation', 'quantite', 'prix_unitaire']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control'}),
        }

ArticleFormSet = inlineformset_factory(Facture, Article, form=ArticleForm, extra=1, can_delete=True)