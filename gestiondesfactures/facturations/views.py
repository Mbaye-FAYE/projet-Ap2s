from datetime import timezone
from email.message import EmailMessage
from multiprocessing.connection import Client
import os
from typing import Self
from django.db import IntegrityError
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
import weasyprint
from .models import Facture, Article    # Importer les modèles Facture et Article
from .forms import ArticleFormSet, FactureForm, ArticleForm, ClientForm # Importer les formulaires
from .utils import generate_facture_pdf, send_facture_email # Importer les fonctions utilitaires
from django.http import JsonResponse # Pour renvoyer des réponses JSON
from django.template.loader import render_to_string
import base64
from decimal import Decimal
from .forms import FactureForm, ClientForm
from .models import Facture, Article
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
import os
from weasyprint import HTML
from django.utils import timezone
import random  # Si tu veux générer un numéro unique par hasard
from .models import Facture, FactureGlobale
from num2words import num2words
from django.utils.timezone import now

def preview_facture_pdf(request):
    if request.method == "POST":
        data = request.POST
        html_content = render_to_string("facture_pdf.html", {"facture": data})  # Utilisation de facture_pdf.html
        
        pdf_content = generate_facture_pdf(html_content)  # Génération du PDF
        encoded_pdf = base64.b64encode(pdf_content).decode('utf-8')  # Encodage en Base64

        return JsonResponse({"pdf_data": encoded_pdf})
    return JsonResponse({"error": "Requête invalide"}, status=400)


def index(request):
    factures = Facture.objects.all()

    numero = request.GET.get('numero')
    client = request.GET.get('client')
    date_emission = request.GET.get('date_emission')

    if numero:
        factures = factures.filter(numero__icontains=numero)
    
    if client:
        factures = factures.filter(client__nom__icontains=client)
    
    if date_emission:
        factures = factures.filter(date_emission=date_emission)

    return render(request, 'index.html', {'factures': factures})


def facture_detail(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    articles = facture.articles.all()  # Récupérer tous les articles liés à la facture

    print(f"Articles associés à la facture: {articles}")  # Ajout du debug pour vérifier les articles

    return render(request, 'facture_detail.html', {
        'facture': facture,
        'articles': articles  # S'assurer que les articles sont passés au template
    })


def facture_create(request):
    if request.method == 'POST':
        form = FactureForm(request.POST)
        client_form = ClientForm(request.POST)
        formset = ArticleFormSet(request.POST)

        if form.is_valid() and client_form.is_valid() and formset.is_valid():
            client = client_form.save()
            facture = form.save(commit=False)
            facture.client = client
            facture.save()

            articles = formset.save(commit=False)
            for article in articles:
                article.facture = facture
                article.save()

            messages.success(request, f"Facture {facture.numero} et son client ont été créés avec succès !")
            return redirect('facture_detail', facture_id=facture.id)
        else:
            print("Erreurs FactureForm:", form.errors)
            print("Erreurs ClientForm:", client_form.errors)
            print("Erreurs ArticleFormSet:", formset.errors)
            messages.error(request, "Erreur lors de la création de la facture et du client.")
    else:
        form = FactureForm()
        client_form = ClientForm()
        formset = ArticleFormSet()

    return render(request, 'facture_form.html', {'form': form, 'client_form': client_form, 'formset': formset})




def facture_update(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    client = facture.client  # Récupérer le client lié à la facture
    ArticleFormSet = inlineformset_factory(Facture, Article, form=ArticleForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture)  # Charger la facture existante
        client_form = ClientForm(request.POST, instance=client)  # Charger le client existant
        formset = ArticleFormSet(request.POST, instance=facture)  # Charger les articles existants

        if form.is_valid() and client_form.is_valid() and formset.is_valid():
            client = client_form.save()  # Mettre à jour le client
            facture = form.save(commit=False)
            facture.client = client
            facture.save()

            articles = formset.save(commit=False)
            for article in articles:
                article.facture = facture
                article.save()

            messages.success(request, f"Facture {facture.numero} mise à jour avec succès !")
            return redirect('facture_detail', facture_id=facture.id)

        else:
            messages.error(request, "Erreur lors de la modification de la facture.")
            print("Erreurs :", form.errors, formset.errors, client_form.errors)  # Debugging

    else:
        form = FactureForm(instance=facture)  # Pré-remplir la facture
        client_form = ClientForm(instance=client)  # Pré-remplir le client
        formset = ArticleFormSet(instance=facture)  # Pré-remplir les articles

    return render(request, 'facture_form.html', {
        'form': form,
        'client_form': client_form,
        'formset': formset,
        'facture': facture
    })


def facture_delete(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    
    if request.method == 'POST':
        facture.delete()
        messages.success(request, f"Facture {facture.numero} supprimée avec succès !")
        return redirect('index')
    
    return render(request, 'facture_confirm_delete.html', {'facture': facture})


def ajouter_article(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.facture = facture

            # Calculer le total HT en utilisant la méthode du modèle
            article.save()

            messages.success(request, "Article ajouté avec succès !")
            return redirect('facture_detail', facture_id=facture.id)
        else:
            messages.error(request, "Erreur lors de l'ajout de l'article.")
    
    else:
        form = ArticleForm()
    
    return render(request, 'ajouter_article.html', {'form': form, 'facture': facture})


def supprimer_article(request, facture_id, article_id):
    article = get_object_or_404(Article, id=article_id, facture_id=facture_id)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, "Article supprimé avec succès !")
        return redirect('facture_detail', facture_id=facture_id)
    
    return render(request, 'supprimer_article.html', {'article': article})

def convertir_montant_en_lettres(montant):
    return num2words(montant, lang='fr').capitalize() + " francs CFA"

def generate_pdf(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    
    try:
        # Vérifier que total_ttc est défini
        total_ttc = facture.total_ttc if facture.total_ttc else 0

        # Conversion du montant total en lettres
        total_ttc_en_lettres = convertir_montant_en_lettres(total_ttc)

        # Générer le HTML de la facture avec le montant en lettres
        html_content = render_to_string('facture_pdf.html', {
            'facture': facture,
            'total_ttc_en_lettres': total_ttc_en_lettres,  # Ajout du montant en lettres
        })

        # Charger un fichier CSS pour améliorer le design du PDF
        css = weasyprint.CSS(string='''
            @page { size: A4; margin: 20mm; }
            body { font-family: Arial, sans-serif; font-size: 12px; }
            h1 { color: #333; text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        ''')

        # Générer le PDF avec les styles CSS
        pdf = weasyprint.HTML(string=html_content).write_pdf(stylesheets=[css])

        # Retourner la réponse avec le PDF pour téléchargement
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="facture_{facture.numero}.pdf"'

        return response

    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF : {e}", status=500)

def generate_pdf_file(facture):
    """Génère un fichier PDF et retourne son chemin."""
    html_content = render_to_string('facture_pdf.html', {'facture': facture})
    
    pdf_file_path = f"facture_{facture.numero}.pdf"
    
    # Générer le PDF et enregistrer le fichier temporairement
    with open(pdf_file_path, "wb") as pdf_file:
        pdf_file.write(weasyprint.HTML(string=html_content).write_pdf())

    return pdf_file_path

def send_facture(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)

    # Générer le PDF temporaire
    pdf_file_path = generate_pdf_file(facture)

    if not pdf_file_path:
        messages.error(request, "Erreur lors de la génération du PDF.")
        return redirect('facture_detail', facture_id=facture.id)

    # Vérifier si le client a une adresse e-mail
    recipient_email = facture.client.email
    if not recipient_email:
        messages.error(request, "Le client n'a pas d'adresse e-mail.")
        return redirect('facture_detail', facture_id=facture.id)

    # Construire le contenu de l'email
    subject = f"Facture {facture.numero} - {facture.client.nom}"
    message_html = render_to_string('emails/facture_email.html', {'facture': facture})
    message_text = strip_tags(message_html)  # Convertir en texte brut

    # Configurer l'e-mail
    email = EmailMessage(
        subject,
        message_text,
        "faye86712@gmail.com",  # Remplace par ton e-mail d'expéditeur
        [recipient_email]
    )

    # Ajouter le PDF en pièce jointe
    try:
        with open(pdf_file_path, 'rb') as pdf_file:
            email.attach(f"Facture_{facture.numero}.pdf", pdf_file.read(), "application/pdf")

        email.send()
        messages.success(request, "Facture envoyée avec succès !")

    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi de l'e-mail : {e}")

    finally:
        # Supprimer le fichier temporaire après l'envoi
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)

    return redirect('facture_detail', facture_id=facture.id)

def facture_list(request):
    factures = Facture.objects.all()
    return render(request, 'facture_list.html', {'factures': factures})
    


def create_facture_globale(request):
    if request.method == "POST":
        # Récupérer les factures sélectionnées depuis le formulaire
        selected_factures = request.POST.getlist('factures')

        if selected_factures:
            try:
                # Générer un numéro unique pour la facture globale
                # Tu peux utiliser un simple générateur ou une logique d'incrémentation
                unique_number = f"FG-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
                
                # Créer la facture globale avec une date d'émission par défaut et un numéro unique
                facture_globale = Facture.objects.create(
                    numero=unique_number,  # Le numéro généré
                    client=None,  # Assigner le client approprié ou laisser None
                    total_ttc=0,  # Ce total sera calculé plus tard
                    date_emission=timezone.now()  # Assigner la date actuelle à la facture globale
                )
                
                total_globale = 0
                for facture_id in selected_factures:
                    facture = Facture.objects.get(id=facture_id)
                    total_globale += facture.total_ttc  # Calculer le total global

                facture_globale.total_ttc = total_globale
                facture_globale.save()

                # Après avoir créé la facture globale, on peut rediriger l'utilisateur pour télécharger le PDF
                return redirect('generate_pdf_facture_globale', facture_id=facture_globale.id)

            except IntegrityError as e:
                # Si une erreur d'intégrité se produit, tu peux gérer ici
                return HttpResponse(f"Erreur d'intégrité : {str(e)}", status=400)

    # Si ce n'est pas un POST, afficher la page de sélection
    factures = Facture.objects.all()  # Récupérer toutes les factures disponibles
    return render(request, 'select_factures_globale.html', {'factures': factures})

#def convertir_montant_en_lettres(montant):
   # return num2words(Self.montant, to='currency', lang='fr').capitalize() + " francs CFA"

def generate_pdf_facture_globale(request, facture_id):
    # Récupérer la facture globale
    facture_globale = get_object_or_404(FactureGlobale, id=facture_id)

    # Trier les factures par numéro ou autre critère pertinent
    factures = facture_globale.factures.all().order_by('numero')  # Tri par numéro de facture

    # Vérifier qu'il y a au moins une facture et récupérer le client de la première facture
    client_nom = factures[0].client.nom if factures.exists() else None  

    # Calcul des totaux
    total_general_ht = sum(facture.total_ht for facture in factures)
    total_tva = sum(facture.tva for facture in factures)
    total_general_ttc = sum(facture.total_ttc for facture in factures)

    # Conversion en lettres
    total_ttc_en_lettres = convertir_montant_en_lettres(total_general_ttc)

    # Générer le HTML pour la facture globale
    html_string = render_to_string('facture_globale_pdf.html', {
        'facture_globale': facture_globale,
        'factures': factures,
        'total_general_ht': total_general_ht,
        'total_tva': total_tva,
        'total_general_ttc': total_general_ttc,
        'total_ttc_en_lettres': total_ttc_en_lettres,  # Ajout du montant en lettres
        'client_nom': client_nom,
        'date_actuelle': now(),
    })

    # Générer le PDF
    html = weasyprint.HTML(string=html_string)
    pdf_file = html.write_pdf()

    # Réponse HTTP pour le téléchargement du PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=facture_globale_{facture_globale.id}.pdf'

    return response

def select_factures_globale(request):
    factures = Facture.objects.all()

    if request.method == "POST":
        facture_ids = request.POST.getlist("factures")  # Récupérer les factures sélectionnées
        if not facture_ids:
            return render(request, 'select_factures_globale.html', {'factures': factures, 'error': "Veuillez sélectionner au moins une facture."})

        factures_selectionnees = Facture.objects.filter(id__in=facture_ids)

        if not factures_selectionnees.exists():
            return render(request, 'select_factures_globale.html', {'factures': factures, 'error': "Factures non trouvées."})

        client = factures_selectionnees.first().client  # Prendre le client de la première facture sélectionnée

        facture_globale = FactureGlobale.objects.create(client=client)
        facture_globale.factures.set(factures_selectionnees)

        return redirect('facture_globale_detail', facture_globale.id)  # Redirection vers la page de détail

    return render(request, 'select_factures_globale.html', {'factures': factures})


def facture_globale_detail(request, facture_globale_id):
    facture_globale = get_object_or_404(FactureGlobale, id=facture_globale_id)
    factures = facture_globale.factures.all()

    return render(request, 'facture_globale_detail.html', {
        'facture_globale': facture_globale,
        'factures': factures
    })