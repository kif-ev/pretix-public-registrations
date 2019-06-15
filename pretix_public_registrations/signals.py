from django import forms
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _, get_language
from django_gravatar.helpers import get_gravatar_url
from i18nfield.strings import LazyI18nString
from pretix.presale.signals import question_form_fields, front_page_bottom, process_response
from pretix.base.models import OrderPosition


@receiver(question_form_fields, dispatch_uid="public_registration_question")
def add_public_registration_question(sender, **kwargs):
    return {'public_registration': forms.CharField(
        label=_('Public registration'),
        required=False,
        help_text=sender.settings.get('public_registration_field_help_text', as_type=LazyI18nString),
        widget=forms.CheckboxInput(),
    )}


@receiver(signal=front_page_bottom, dispatch_uid="public_registrations_table")
def add_public_registrations_table(sender, **kwargs):
    cached = sender.cache.get('public_registrations_table_' + get_language())
    if cached is None:
        cached = ""
        headers = ["", "Name"]
        order_positions = OrderPosition.all.filter(order__event=sender)
        public_order_positions = [
            op for op in order_positions
            if op.meta_info_data.get('question_form_data', {}).get('public_registration') == "True"
        ]
        public_registrations = [
            {
                'gr_url': get_gravatar_url(pop.attendee_email, size=24, default="wavatar"),
                'fields': [pop.attendee_name_cached]
            } for pop in public_order_positions
        ]
        template = get_template('pretix_public_registrations/front_page.html')
        cached = template.render({
            'headers': headers,
            'public_registrations': public_registrations
        })
    return cached


@receiver(signal=process_response, dispatch_uid="public_registragions_csp_headers")
def add_public_registrations_csp_headers(sender, **kwargs):
    response = kwargs['response']
    response['Content-Security-Policy'] = "img-src https://secure.gravatar.com"
    return response
