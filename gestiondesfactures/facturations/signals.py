from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article

@receiver(post_save, sender=Article)
@receiver(post_delete, sender=Article)
def update_facture_totaux(sender, instance, **kwargs):
    instance.facture.calculer_totaux()
