from django import forms
from django.utils.translation import ugettext_lazy as _
from pretix.base.forms import SettingsForm


class PublicRegistrationsForm(SettingsForm):
    public_registrations_items = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'scrolling-multiple-choice'}
        ),
        label=_('Show public registrations for'),
        required=True,
        choices=[],
    )
    public_registrations_questions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'scrolling-multiple-choice'}
        ),
        label=_('Publicly show answers for'),
        required=True,
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['public_registrations_items'].choices = [
            (i.pk, i.name) for i in self.obj.items.all()
        ]
        self.fields['public_registrations_questions'].choices = [
            (q.pk, q.question) for q in self.obj.questions.all()
        ]
