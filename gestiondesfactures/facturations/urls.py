from django.urls import path
from . import views
from .views import facture_list, preview_facture_pdf, create_facture_globale, generate_pdf_facture_globale, select_factures_globale, facture_globale_detail

urlpatterns = [
    # Routes de factures classiques
    path('', views.index, name='index'),  # Page d'accueil avec la liste des factures
    path('facture/<int:facture_id>/', views.facture_detail, name='facture_detail'),  # Affichage détail
    path('facture/nouvelle/', views.facture_create, name='facture_create'),  # Ajouter une facture
    path('facture/<int:facture_id>/modifier/', views.facture_update, name='facture_update'),  # Modifier une facture
    path('facture/<int:facture_id>/supprimer/', views.facture_delete, name='facture_delete'),  # Supprimer une facture
    path('facture/<int:facture_id>/pdf/', views.generate_pdf, name='generate_pdf'),  # Générer un PDF
    path('facture/<int:facture_id>/envoyer/', views.send_facture, name='send_facture'),  # Envoyer la facture par email
    path('factures/', facture_list, name='facture_list'),
    path("facture/preview_pdf/", preview_facture_pdf, name="preview_facture_pdf"),
    path('facture/<int:facture_id>/article/<int:article_id>/supprimer/', views.supprimer_article, name='supprimer_article'),
    path('facture/<int:facture_id>/ajouter_article/', views.ajouter_article, name='ajouter_article'),
    path('facture/<int:facture_id>/preview/', views.preview_facture_pdf, name='preview_facture_pdf'),

    # Nouveau: Créer une facture globale
    path('facture/globale/creer/', views.create_facture_globale, name='create_facture_globale'), # Créer la facture globale
    path('facture/globale/<int:facture_id>/pdf/', views.generate_pdf_facture_globale, name='generate_pdf_facture_globale'),
    path('facture/globale/select/', select_factures_globale, name='select_factures_globale'),
    path('facture/globale/<int:facture_globale_id>/', facture_globale_detail, name='facture_globale_detail'),
]
