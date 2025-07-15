from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Client, Facture, Article

class ArticleInline(admin.TabularInline):  
    model = Article  
    extra = 1  # Permet d'ajouter des articles directement dans l'admin

class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero', 'client', 'date_emission', 'total_ttc')
    search_fields = ('numero', 'client__nom')
    list_filter = ('date_emission',)
    inlines = [ArticleInline]

class ClientAdmin(admin.ModelAdmin):
    list_display = ('code_client', 'nom', 'email', 'telephone')
    search_fields = ('nom', 'email')
    
admin.site.register(Client, ClientAdmin)
admin.site.register(Facture, FactureAdmin)
