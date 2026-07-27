from django.db import migrations


def create_content_editor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    group, _ = Group.objects.get_or_create(name="内容编辑")
    app_permissions = Permission.objects.filter(
        content_type__app_label__in=("products", "news"),
        codename__regex=r"^(add|change|view)_",
    )
    group.permissions.set(app_permissions)


def remove_content_editor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="内容编辑").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
        ("news", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_content_editor_group, remove_content_editor_group),
    ]
