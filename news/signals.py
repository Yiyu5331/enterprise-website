from django.db.models.signals import post_delete
from django.dispatch import receiver

from main.content_utils import delete_field_file

from .models import Article


@receiver(post_delete, sender=Article)
def delete_article_images(sender, instance, **kwargs):
    delete_field_file(instance.cover)
    delete_field_file(instance.cover_web)
    delete_field_file(instance.cover_thumb)
