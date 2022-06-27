# Generated by Django 3.2.13 on 2022-06-27 10:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import odk.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='XFormSubmit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_id', models.SlugField(editable=False, help_text='Retrieved from XML form (settings tab of Excel file)', max_length=200)),
                ('version', models.CharField(editable=False, help_text='Retrieved from XML form (settings tab of Excel file)', max_length=200)),
                ('instanceid', models.UUIDField(unique=True)),
                ('deviceid', models.CharField(blank=True, max_length=255, null=True)),
                ('survey_date', models.DateField(blank=True, null=True, verbose_name='Encoding date')),
                ('picture_files', models.JSONField(blank=True, null=True, verbose_name='Picture file names')),
                ('xml_file', models.FileField(blank=True, help_text='XML file sended through ODK Collect Mobile App', upload_to='', verbose_name='Submitted form')),
                ('xml_content', models.TextField(help_text='XML content sended through ODK Collect Mobile App', verbose_name='Content of XML file submitted')),
                ('submitted_by', models.CharField(blank=True, max_length=255, null=True, verbose_name='Submitted by')),
                ('submitted_on', models.DateTimeField(auto_now_add=True, verbose_name='Submitted on')),
                ('inserted_on', models.DateTimeField(blank=True, null=True, verbose_name='Inserted on')),
            ],
            options={
                'verbose_name': 'Submitted form',
                'verbose_name_plural': 'Submitted forms',
                'ordering': ('submitted_on',),
            },
        ),
        migrations.CreateModel(
            name='XForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xls_file', models.FileField(blank=True, help_text='XLSForm with 3 tabs: survey, choices, settings', null=True, upload_to=odk.models.xform_path, verbose_name='Excel file')),
                ('xml_file', models.FileField(blank=True, help_text="XLSForm converted by <a href='https://getodk.org/xlsform/' target='_blank'>https://getodk.org/xlsform/</a>", null=True, upload_to=odk.models.xform_path, verbose_name='XML file')),
                ('xml_content', models.TextField(blank=True, null=True, verbose_name='Content of XML form')),
                ('form_id', models.SlugField(editable=False, help_text='Retrieved from XLSForm (xls settings tab)', max_length=200)),
                ('version', models.CharField(editable=False, help_text='Retrieved from XLSForm (xls settings tab)', max_length=200)),
                ('title', models.CharField(editable=False, help_text='Retrieved from XLSForm (xls settings tab)', max_length=250, verbose_name='Title')),
                ('short_desc', models.CharField(blank=True, max_length=250, verbose_name='Short description')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
                ('model_created_on', models.DateTimeField(blank=True, null=True, verbose_name='Model created on')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='xform_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
            ],
            options={
                'verbose_name': 'Available form',
                'ordering': ('xml_file',),
                'unique_together': {('form_id', 'version')},
            },
        ),
    ]
