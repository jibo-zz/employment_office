import json

from django.db import models
from django.forms import FileField, RegexField
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.core.fields import RichTextField
from wagtail.contrib.forms.models import (
    AbstractEmailForm, AbstractFormField, FORM_FIELD_CHOICES)
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.documents.models import get_document_model
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel

from phonenumber_field.formfields import PhoneNumberField


def filename_to_title(filename):
    from os.path import splitext
    if filename:
        result = splitext(filename)[0]
        result = result.replace('-', ' ').replace('_', ' ')
        return result.title()


class FormField(AbstractFormField):
    CHOICES = FORM_FIELD_CHOICES + \
        (('document', 'Upload Document'), ('phone', 'Phone'),)
    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=CHOICES)

    page = ParentalKey('FormPage', on_delete=models.CASCADE,
                       related_name='custom_form_fields')


class ExtendedFormBuilder(FormBuilder):
    def create_document_field(self, field, options):
        return FileField(**options)

    def create_phone_field(self, field, options):
        return RegexField(regex=r'^\+253?|77?|21?\d{8,12}$')


class FormPage(AbstractEmailForm):
    form_builder = ExtendedFormBuilder

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro', classname="full"),
        InlinePanel('custom_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    def process_form_submission(self, form):
        cleaned_data = form.cleaned_data

        for name, field in form.fields.items():
            if isinstance(field, FileField):
                document_file_data = cleaned_data[name]
                if document_file_data:
                    DocumentModel = get_document_model()
                    for name, field in form.fields.items():
                        if name == 'full-name':
                            title_file_data = cleaned_data[name]
                            if title_file_data:
                                document = DocumentModel(
                                    file=document_file_data,
                                    title=title_file_data,
                                )
                                document.save()
                                cleaned_data.update({name: document.title})
                            else:
                                document = DocumentModel(
                                    file=cleaned_data[name],
                                    title=filename_to_title(
                                        cleaned_data[name].name),
                                    # assumes there is always a user - will fail otherwise
                                    # uploaded_by_user=form.user,
                                )
                                document.save()
                                cleaned_data.update({name: document.title})
                else:
                    # remove the value from the data
                    del cleaned_data[name]

        return self.get_submission_class().objects.create(
            form_data=json.dumps(cleaned_data, cls=DjangoJSONEncoder),
            page=self,
        )

    def get_form_fields(self):
        return self.custom_form_fields.all()
