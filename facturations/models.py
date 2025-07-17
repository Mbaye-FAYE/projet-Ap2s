from django.db import models
from decimal import Decimal
from num2words import num2words


class Client(models.Model):
    code_client = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return self.nom

from django.db import models
from django.utils.timezone import now

class Facture(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_emission = models.DateField()
    numero_commande = models.CharField(max_length=50, blank=True, null=True)
    livraison = models.CharField(max_length=200, blank=True, null=True)
    
    # Modification de la précision et de l'échelle des champs décimaux
    total_ht = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tva = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_ttc = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    arrete_somme = models.CharField(max_length=200, blank=True, null=True)

    # Ajout du champ est_globale pour indiquer si la facture est globale
    est_globale = models.BooleanField(default=False)  # Par défaut, une facture n'est pas globale

    def __str__(self):
        return f"Facture {self.numero} - {self.client.nom}"
    
    def calculer_totaux(self):
        total_ht = sum(article.total_ht() for article in self.articles.all())
        tva = total_ht * Decimal('0.18')
        total_ttc = total_ht + tva

        self.total_ht = total_ht
        self.tva = tva
        self.total_ttc = total_ttc

        # Conversion du total TTC en lettres et mise à jour du champ arrete_somme
        self.arrete_somme = num2words(self.total_ttc, to='currency', lang='fr')  # Utilisation de 'currency' pour obtenir la conversion en CFA
        
        self.save()

    def save(self, *args, **kwargs):
        if not self.numero:  # Générer un numéro de facture seulement si ce n'est pas déjà fait
            # Récupérer l'année et le mois de la date d'émission
            annee_mois = self.date_emission.strftime('%Y%m')
            
            # Récupérer le dernier numéro de facture pour ce client et année/mois
            last_facture = Facture.objects.filter(client=self.client, date_emission__year=self.date_emission.year, date_emission__month=self.date_emission.month).order_by('-numero')
            
            # Si aucune facture n'existe pour ce mois/année, commencer à 1
            if last_facture.exists():
                last_num = int(last_facture[0].numero.split('-')[-1])
                next_num = last_num + 1
            else:
                next_num = 1

            # Générer le numéro de facture
            self.numero = f"{annee_mois}-{next_num:03d}"  # Format : "YYYYMM-001"
        
        super().save(*args, **kwargs)




class Article(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='articles')
    quantite = models.PositiveIntegerField()
    designation = models.CharField(max_length=200)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def total_ht(self):
        return self.quantite * self.prix_unitaire

class FactureGlobale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    factures = models.ManyToManyField(Facture, related_name='factures_globales')  
    date_creation = models.DateTimeField(auto_now_add=True)

    def total_ht(self):
        return sum(facture.total_ht for facture in self.factures.all())

    def tva(self):
        return sum(facture.tva for facture in self.factures.all())

    def total_ttc(self):
        return sum(facture.total_ttc for facture in self.factures.all())

    def arrete_somme(self):
        return num2words.num2words(self.total_ttc(), to='currency', lang='fr')

    def __str__(self):
        return f"Facture Globale {self.id} - {self.client.nom}"

