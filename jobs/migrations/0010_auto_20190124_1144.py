# Generated by Django 2.1.5 on 2019-01-24 08:44

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_auto_20190119_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_form_fields', to='jobs.FormPage'),
        ),
    ]
