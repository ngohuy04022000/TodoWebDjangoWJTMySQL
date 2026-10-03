from django.db import migrations, models
import django.utils.timezone
import todo.models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_alter_todoitem_created_date_alter_todoitem_due_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlist',
            name='email',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userlist',
            name='password',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='due_date',
            field=models.DateTimeField(default=todo.models.default_due_date),
        ),
        migrations.AlterField(
            model_name='todoitem',
            name='modification_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
