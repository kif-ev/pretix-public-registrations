from django import forms
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from i18nfield.strings import LazyI18nString
from pretix.presale.signals import question_form_fields


@receiver(question_form_fields, dispatch_uid="pretix_public_registration_question")
def add_public_registration_question(sender, **kwargs):
    return {'public_registration': forms.CharField(
        label=_('Public registration'),
        required=False,
        help_text=sender.settings.get('public_registration_field_help_text', as_type=LazyI18nString),
        widget=forms.CheckboxInput(),
    )}
