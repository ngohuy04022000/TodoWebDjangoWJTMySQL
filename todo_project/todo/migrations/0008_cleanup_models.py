from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import todo.models


def fill_null_descriptions(apps, schema_editor):
    ToDoItem = apps.get_model("todo", "ToDoItem")
    ToDoItem.objects.filter(description__isnull=True).update(description="")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('todo', '0007_todolist_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todolist',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='todo_lists',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='todolist',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterModelOptions(
            name='todolist',
            options={'ordering': ['title']},
        ),
        migrations.AddConstraint(
            model_name='todolist',
            constraint=models.UniqueConstraint(
                fields=('owner', 'title'), name='unique_list_title_per_owner'
            ),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='id',
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
            ),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='task',
            field=models.CharField(max_length=200),
        ),
        migrations.RunPython(fill_null_descriptions, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='todoitem',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='modification_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='due_date',
            field=models.DateTimeField(default=todo.models.default_due_date),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='todo_list',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='todo.todolist',
            ),
        ),
        migrations.DeleteModel(
            name='UserList',
        ),
    ]
