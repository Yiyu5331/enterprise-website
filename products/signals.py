from django.db.models.signals import post_delete
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from main.content_utils import delete_field_file

from .models import Product, ProductCategory, ProductDocument, ProductGalleryImage


@receiver(post_migrate)
def sync_content_editor_permissions(sender, **kwargs):
    if sender.label != "products":
        return
    from django.contrib.auth.models import Group, Permission

    group, _ = Group.objects.get_or_create(name="内容编辑")
    permissions = Permission.objects.filter(
        content_type__app_label__in=("products", "news"),
        codename__regex=r"^(add|change|view)_",
    )
    group.permissions.set(permissions)


@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=ProductCategory)
@receiver(post_delete, sender=ProductGalleryImage)
def delete_product_images(sender, instance, **kwargs):
    delete_field_file(instance.image)
    delete_field_file(instance.image_web)
    delete_field_file(instance.image_thumb)


@receiver(post_delete, sender=ProductDocument)
def delete_product_document(sender, instance, **kwargs):
    delete_field_file(instance.file)
