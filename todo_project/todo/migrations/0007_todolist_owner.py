from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_existing_lists(apps, schema_editor):
    """Give lists created before per-user ownership existed an owner.

    They go to the oldest superuser, or the oldest user if there is none.
    Lists that cannot be assigned (no users at all) would be unreachable,
    so they are removed.
    """
    ToDoList = apps.get_model("todo", "ToDoList")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    orphans = ToDoList.objects.filter(owner__isnull=True)
    if not orphans.exists():
        return
    owner = (
        User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    if owner is None:
        orphans.delete()
    else:
        orphans.update(owner=owner)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('todo', '0006_userlist_fields_and_callable_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='todolist',
            name='owner',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='todo_lists',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_existing_lists, migrations.RunPython.noop),
    ]
