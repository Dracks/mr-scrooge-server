# Generated by Django 2.0.8 on 2018-11-22 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_auto_20181122_1656'),
    ]

    database_operations = [

    ]

    state_operations = [
        migrations.AddField(
            model_name='tag',
            name='values',
            field=models.ManyToManyField(related_name='tags', through='management.ValuesToTag', to='core.RawDataSource'),
        ),
        migrations.AlterField(
            model_name='valuestotag',
            name='raw_data_source',
            field=models.ForeignKey(on_delete=None, to='core.RawDataSource'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations = database_operations, 
            state_operations = state_operations)
    ]
