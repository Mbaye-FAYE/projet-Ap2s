from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.core.mail import EmailMessage
from num2words import num2words
from django.http import HttpResponse




def montant_en_lettres(montant):
    return num2words(montant, lang='fr') + " francs CFA"

def generate_facture_pdf(facture):
    html_string = render_to_string('facture_pdf.html', {'facture': facture})
    
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        HTML(string=html_string).write_pdf(temp_file.name)
        temp_file.seek(0)
        return temp_file.read()
    
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_pdf:
        HTML(string=html_string).write_pdf(temp_pdf.name)
        return temp_pdf.read()

def send_facture_email(facture, recipient_email):
    pdf_content = generate_facture_pdf(facture)
    email = EmailMessage(
        subject=f"Facture {facture.numero}",
        body="Veuillez trouver votre facture en pièce jointe.",
        to=[recipient_email]
    )
    email.attach(f"facture_{facture.numero}.pdf", pdf_content, "application/pdf")
    email.send()

def convertir_en_lettres(montant):
    """
    Convertir un montant en chiffres en lettres.
    Exemple : 123.45 -> "cent vingt-trois francs quarante-cinq"
    """
    montant_int = int(montant)  # Partie entière
    montant_decimale = int((montant - montant_int) * 100)  # Partie décimale (centimes)

    # Convertir la partie entière en lettres
    montant_lettres = num2words(montant_int, lang='fr')

    # Ajouter la partie décimale si elle existe
    if montant_decimale > 0:
        montant_lettres += f" virgule {num2words(montant_decimale, lang='fr')}"

    return montant_lettres
