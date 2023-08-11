# Generated by Django 4.2.3 on 2023-08-07 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skins', '0004_alter_type_gun_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='skin',
            old_name='float_gun',
            new_name='price',
        ),
        migrations.RemoveField(
            model_name='skin',
            name='type_gun',
        ),
        migrations.AlterField(
            model_name='type_gun',
            name='id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False),
        ),
    ]